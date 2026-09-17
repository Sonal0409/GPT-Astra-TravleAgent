from types import SimpleNamespace
import json
import pytest
from agent import Session, run_agent
from travel import calculate
from app import app

C = dict(destination='Singapore',people=4,days=5,budget=150000,preferences='sightseeing and food',assumptions='Mumbai; flexible dates')
def prepared():
    s=Session()
    s.execute('understand_goal',C.copy())
    s.execute('search_flights',{'scope':'all'})
    s.execute('search_hotels',{'scope':'all'})
    s.execute('estimate_expenses',{})
    return s

def test_prices():
    assert calculate(C,'F1','H1','E1')['total']==185000
    assert calculate(C,'F2','H2','E2')['total']==143000
    assert calculate(dict(C,people=5),'F2','H2','E2')['rooms']==3

def test_completion_guards():
    s=prepared()
    a=dict(flight_id='F1',hotel_id='H1',expense_id='E1',summary='test',tradeoffs='test',itinerary=[])
    with pytest.raises(ValueError): s.execute('complete_plan',a)
    s.execute('check_budget',{k:a[k] for k in ['flight_id','hotel_id','expense_id']})
    with pytest.raises(ValueError): s.execute('complete_plan',a)
    with pytest.raises(ValueError): s.execute('understand_goal',C)

def test_unseen_options():
    s=Session();s.execute('understand_goal',C)
    with pytest.raises(ValueError): s.execute('check_budget',dict(flight_id='F2',hotel_id='H2',expense_id='E2'))

def test_routes():
    c=app.test_client()
    assert c.get('/').status_code==200
    assert c.get('/api/health').json['status']=='ok'
    assert c.post('/api/run',json={'goal':'x'}).status_code==400

def test_tool_outputs_return_to_model():
    class FakeResponses:
        def __init__(self): self.n=0
        def create(self,**kw):
            self.n+=1
            if self.n==1: name,args='understand_goal',C
            else:
                outputs=[x for x in kw['input'] if isinstance(x,dict) and x.get('type')=='function_call_output']
                assert json.loads(outputs[-1]['output'])['budget']==150000
                name,args='report_infeasible',{'summary':'Test double only'}
            return SimpleNamespace(output=[SimpleNamespace(type='function_call',name=name,arguments=json.dumps(args),call_id=str(self.n))])
    assert list(run_agent('test',client=SimpleNamespace(responses=FakeResponses())))[-1]['type']=='infeasible'

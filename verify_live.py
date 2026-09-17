"""Real API integration test; saves public tool evidence, never private reasoning."""
import json
from pathlib import Path
from agent import run_agent

events=[]
for event in run_agent('Plan a 5-day Singapore trip for 4 people under ₹1,50,000. We like sightseeing and good food.'):
    events.append(event)
    print(event['type'],event.get('tool',''),event.get('message','').encode('ascii','replace').decode(),event.get('total',''),flush=True)
Path('artifacts').mkdir(exist_ok=True)
Path('artifacts/live-run.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
checks=[e for e in events if e['type']=='budget']
assert checks and checks[0]['total']==185000 and not checks[0]['within_budget'], 'First budget check must fail at 185000'
assert any(e['type']=='action' and e.get('tool')=='announce_strategy' and e['arguments']['phase']=='replan' for e in events), 'No model replanning tool call'
assert events[-1]['type']=='complete', 'No verified completion'
assert events[-1]['verified']['total']<=150000
assert len(events[-1]['itinerary'])==5
assert events[-1]['constraints']['people']==4
print('LIVE API VERIFICATION PASSED. Final total:',events[-1]['verified']['total'])

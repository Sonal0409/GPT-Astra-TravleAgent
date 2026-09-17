"""Deterministic inventory and independently verified INR arithmetic."""
import math

FLIGHTS = {
    'F1': dict(name='Full-service direct', price=22000, detail='Mumbai ↔ Singapore · daytime · checked bag included', tier='recommended'),
    'F2': dict(name='Value direct', price=17000, detail='Mumbai ↔ Singapore · early departure · cabin bag included', tier='alternatives'),
    'F3': dict(name='Connecting economy', price=16000, detail='Mumbai ↔ Singapore · 6-hour connection · cabin bag included', tier='alternatives'),
}
HOTELS = {
    'H1': dict(name='Marina City Hotel', price=6000, detail='Central · private twin room · 2 adults', tier='recommended'),
    'H2': dict(name='Lavender MRT Stay', price=3500, detail='Near MRT · compact private twin room · 2 adults', tier='alternatives'),
    'H3': dict(name='Riverside Boutique', price=4500, detail='Riverside · private twin room · 2 adults', tier='alternatives'),
}
EXPENSES = {
    'E1': dict(name='Classic city experience', food=900, transport=350, activities=2500, detail='Mixed restaurants and hawkers; MRT plus taxis; paid sightseeing'),
    'E2': dict(name='Hawker & heritage explorer', food=900, transport=250, activities=2500, detail='Good hawker food; MRT; Gardens conservatories plus free heritage walks'),
    'E3': dict(name='Premium dining', food=1600, transport=500, activities=4500, detail='Premium restaurants, taxis and additional paid attractions'),
}

def search(kind, scope):
    source = FLIGHTS if kind == 'flights' else HOTELS
    return {'currency': 'INR', 'simulated': True, 'price_basis': 'per person, round trip' if kind == 'flights' else 'per room per night',
            'options': [dict(id=k, **v) for k, v in source.items() if scope == 'all' or v['tier'] == scope],
            'hint': 'Use scope=all to explore the full inventory and compare trade-offs.'}

def calculate(c, flight_id, hotel_id, expense_id):
    f, h, e = FLIGHTS[flight_id], HOTELS[hotel_id], EXPENSES[expense_id]
    p, d = c['people'], c['days']
    items = {'Flights': f['price']*p, 'Hotel': h['price']*math.ceil(p/2)*(d-1),
             'Food': e['food']*p*d, 'Local transport': e['transport']*p*d,
             'Sightseeing': e['activities']*p, 'Visa & insurance allowance': 2500*p, 'Contingency': 4000}
    total = sum(items.values())
    return dict(total=total, budget=c['budget'], remaining=c['budget']-total, within_budget=total <= c['budget'],
                breakdown=items, flight_id=flight_id, hotel_id=hotel_id, expense_id=expense_id,
                flight=f['name'], hotel=h['name'], expenses=e['name'], rooms=math.ceil(p/2), nights=d-1)

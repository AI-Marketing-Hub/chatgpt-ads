"""Offline acceptance fixture only. No networking or native OpenAI payload claim."""
import json,math
from collections import defaultdict

def classify(records):
    groups=defaultdict(list);suppressed=[];rejected=[];excluded=[];held=[]
    for e in records:
        eid=e.get('event_id')
        if e.get('consent')!='granted':suppressed.append(eid);continue
        if e.get('business_event')!='paid_order':excluded.append(eid);continue
        value=e.get('value')
        if not isinstance(eid,str) or not eid or e.get('currency')!='USD' or isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
            rejected.append(eid);continue
        groups[eid].append(e)
    eligible=[]
    for eid,events in groups.items():
        if len({(x['value'],x['currency']) for x in events})!=1:held.append(eid)
        else:eligible.append(eid)
    return {'eligible_ids':sorted(eligible),'suppressed_ids':suppressed,'rejected_ids':rejected,'excluded_ids':excluded,'held_ids':held,'native_events_sent':0,'scope':'offline_business_contract_only'}

def main():
    base={'event_id':'synthetic-order-1','consent':'granted','business_event':'paid_order','currency':'USD','value':40.0}
    cases=[
      ('valid',[base],1,0,0,0),
      ('browser_server_duplicate',[dict(base,channel='browser'),dict(base,channel='server')],1,0,0,0),
      ('conflicting_duplicate',[base,dict(base,value=41.0)],0,0,0,0),
      ('unknown_consent',[dict(base,consent='unknown')],0,1,0,0),
      ('denied_consent',[dict(base,consent='denied')],0,1,0,0),
      ('missing_id',[dict(base,event_id=None)],0,0,1,0),
      ('nonfinite_value',[dict(base,value=float('nan'))],0,0,1,0),
      ('bool_value',[dict(base,value=True)],0,0,1,0),
      ('wrong_currency',[dict(base,currency='EUR')],0,0,1,0),
      ('refund',[dict(base,business_event='refund')],0,0,0,1)]
    outcomes=[]
    for name,rows,a,b,c,d in cases:
        result=classify(rows)
        assert [len(result[k]) for k in ('eligible_ids','suppressed_ids','rejected_ids','excluded_ids')]==[a,b,c,d],name
        assert len(result['held_ids']) == (1 if name=='conflicting_duplicate' else 0), name
        outcomes.append({'case':name,'status':'pass','result':result})
    print(json.dumps({'scope':'offline fixture, not platform behavior','cases':outcomes},indent=2))
if __name__=='__main__':main()

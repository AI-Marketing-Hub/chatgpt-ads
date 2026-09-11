#!/usr/bin/env python3
"""Fail closed on absent, unknown or expired source records. Does not browse."""
import argparse,json,sys
from datetime import date
from pathlib import Path
REGISTRY=Path(__file__).resolve().parents[1]/'references/sources.json'
def check(sources,ids=None,as_of=None):
    as_of=as_of or date.today()
    index={s['id']:s for s in sources}
    selected=list(index) if ids is None else ids
    blocked=[]
    if not selected:blocked.append({'source_id':None,'reason':'no_sources_selected'})
    for sid in selected:
        if sid not in index:
            blocked.append({'source_id':sid,'reason':'unknown_source'});continue
        source=index[sid]
        try:
            retrieved=date.fromisoformat(source['retrieved']);due=date.fromisoformat(source['refresh_due'])
            if retrieved>as_of or due<retrieved:reason='invalid_date_order'
            elif due<as_of:reason='expired'
            else:continue
        except (KeyError,ValueError,TypeError):reason='invalid_date'
        blocked.append({'source_id':sid,'reason':reason})
    return {'status':'blocked' if blocked else 'pass','as_of':as_of.isoformat(),'selected_count':len(selected),'blocked_sources':blocked,'live_verified':False,'scope':'freshness only; current product advice still requires source inspection'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-ids',nargs='+');ap.add_argument('--as-of',help='historical/test date, default actual current date');args=ap.parse_args()
    try:
        day=date.fromisoformat(args.as_of) if args.as_of else None
        result=check(json.loads(REGISTRY.read_text())['sources'],args.source_ids,day)
    except (OSError,ValueError,KeyError,TypeError):
        result={'status':'blocked','reason':'registry_or_date_invalid','live_verified':False}
    print(json.dumps(result,indent=2));return 0 if result['status']=='pass' else 2
if __name__=='__main__':sys.exit(main())

#!/usr/bin/env python3
"""Validate explicit normalized report provenance; native Ads Manager CSV is disabled."""
import argparse,hashlib,importlib.util,json,sys,re
from datetime import date,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from safe_io import read_regular
S=importlib.util.spec_from_file_location('normalized_analyzer',ROOT/'skills/chatgpt-ads/scripts/analyze.py');an=importlib.util.module_from_spec(S);sys.modules[S.name]=an;S.loader.exec_module(an)
def read_report(path,context,expected_account):
 if not isinstance(context,dict):raise ValueError('context must be an object')
 if context.get('profile')!='manual-normalized-v1':raise ValueError('native profile unavailable: exact source mapping and native fixture required')
 required={'profile','account_id','exported_at','source_sha256','source_fields','transformations','mapping_review','granularity','currency','timezone','date_start','date_end','attribution_window','conversion_definition','revenue_basis'}
 if set(context)!=required:raise ValueError('context fields missing or unsupported')
 if not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',expected_account) or context['account_id']!=expected_account:raise ValueError('wrong account')
 if not isinstance(context['mapping_review'],str) or not context['mapping_review'].strip():raise ValueError('mapping review required')
 if not isinstance(context['source_fields'],list) or not context['source_fields'] or not all(isinstance(x,str) and x for x in context['source_fields']):raise ValueError('source fields required')
 if not isinstance(context['transformations'],list) or not all(isinstance(x,str) and x for x in context['transformations']):raise ValueError('explicit transformation list required')
 if not isinstance(context['exported_at'],str):raise ValueError('export timestamp must be a string')
 stamp=datetime.fromisoformat(context['exported_at'].replace('Z','+00:00'))
 if stamp.tzinfo is None:raise ValueError('export timestamp must have timezone')
 if path.is_symlink() or not path.is_file():raise ValueError('regular input file required')
 snapshot=read_regular(path)
 if hashlib.sha256(snapshot).hexdigest()!=context['source_sha256']:raise ValueError('input hash mismatch')
 rows=an.read_normalized_bytes(snapshot)
 for row in rows:
  for key in ('granularity','currency','timezone','date_start','date_end','attribution_window','conversion_definition','revenue_basis'):
   if row.metadata[key]!=context[key]:raise ValueError('context mismatch: '+key)
 result=an.analyze(rows)
 return {'profile':'manual-normalized-v1','account_id':expected_account,'provenance':context,'analysis':result,'native_mapping_verified':False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--csv',type=Path,required=True);p.add_argument('--context',type=Path,required=True);p.add_argument('--account',required=True);a=p.parse_args()
 try:result=read_report(a.csv,json.loads(read_regular(a.context, max_bytes=1024 * 1024)),a.account)
 except (ValueError,OSError,KeyError,TypeError) as e:print('report refused: '+str(e),file=sys.stderr);return 1
 print(json.dumps(result,indent=2,allow_nan=False));return 0
if __name__=='__main__':sys.exit(main())

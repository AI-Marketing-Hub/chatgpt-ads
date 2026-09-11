#!/usr/bin/env python3
"""Generate read-only Markdown evidence views from canonical registries."""
import argparse,json,sys,hashlib,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from safe_io import reject_symlinks,read_regular
import knowledge_core
def views(root, snapshots=None):
 snapshots=snapshots or {name:read_regular(root/name) for name in ('references/source-ledger.json','references/claims.json','references/contradictions.json')}
 sources={s['id']:s for s in json.loads(snapshots['references/source-ledger.json'])['sources']}
 claims=json.loads(snapshots['references/claims.json'])['claims']
 conflicts=json.loads(snapshots['references/contradictions.json'])['contradictions']
 out={}
 for lane in ('platform','measurement','policy','terms'):
  blocks=[f'# {lane.title()} evidence','Generated from canonical registries. Do not edit this projection. Dated documentation is not account verification. Run guarded retrieval before using a current claim.']
  for c in claims:
   if c.get('lane')!=lane:continue
   blocks += ['## '+c['id'],c['claim'],'Evidence state: '+c.get('review_status',c.get('status',c.get('support','unknown')))+'. Availability: '+c.get('availability','unknown')+'.', 'Interpretation: '+c.get('recommendation','No recommendation recorded.')]
   blocks += ['- ['+sources[s]['title']+']('+sources[s]['url']+') (`'+s+'`; retrieved '+str(sources[s].get('retrieved') or 'unknown')+')' for s in c['source_ids'] if s in sources]
  out[f'skills/chatgpt-ads/references/{lane}-findings.md']='\n\n'.join(blocks)+'\n'
 blocks=['# Capability map','Generated navigation. Canonical capability states are in the companion root `references/capabilities.json`. No account has been verified by this package.','\n'.join(f'- [{x.title()} findings]({x}-findings.md)' for x in ('platform','measurement','policy','terms')),'## Conflicts']
 for c in conflicts:blocks+=['### '+c['id'],c.get('details',c.get('observation',c.get('claim_a',''))),c.get('resolution','Unresolved; inspect canonical conflict record.')]
 blocks+=['## Local capabilities','Normalized aggregate analysis and local operating guards are implemented. Browser procedures require available host tools and exact-action authorization. Native API integration and native CSV mapping remain unavailable. Read `sources.json`, `claims.json` and `contradictions.json` for provenance.']
 out['skills/chatgpt-ads/references/capabilities.md']='\n\n'.join(blocks)+'\n'
 return out
def render(root,check=False):
 snapshots={name:read_regular(root/name) for name in ('references/source-ledger.json','references/claims.json','references/contradictions.json')}
 guards={name:hashlib.sha256(data).hexdigest() for name,data in snapshots.items()}
 expected=views(root,snapshots);drift=[];base={};target_bytes={}
 for name,body in expected.items():
  path=reject_symlinks(root/name)
  old=read_regular(path) if path.exists() else None
  if old!=body.encode():drift.append(name)
  base[name]=hashlib.sha256(old).hexdigest() if old is not None else None
  target_bytes[name]=body.encode()
 if check:return {'status':'fail' if drift else 'pass','drift':drift}
 if drift:
  knowledge_core._transaction_commit(root,action='render_views',transaction_id='render-'+uuid.uuid4().hex,base_hashes=base,target_bytes=target_bytes,guard_hashes=guards)
 return {'status':'pass','drift':[]}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
 try:result=render(ROOT,a.check)
 except (ValueError,OSError) as e:print(json.dumps({'status':'fail','error':str(e)}));return 1
 print(json.dumps(result));return result['status']!='pass'
if __name__=='__main__':sys.exit(main())

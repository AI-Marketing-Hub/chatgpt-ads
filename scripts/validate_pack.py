#!/usr/bin/env python3
"""Validate active evidence, interfaces, links and portable projections."""
import json,re,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 errors=[];checks=[];entries=[]
 try:
  if (ROOT/"PUBLIC_PROJECTION.json").exists():
   from package_release import selected
  else:
   from prepare_public import selected
  entries=list(selected(ROOT));checks.append({'package_preflight_files':len(entries),'returncode':0})
 except (ValueError,OSError) as e:errors.append('package preflight: '+str(e))
 for cmd in [['knowledge_core.py','validate'],['knowledge_core.py','sync-projection','--check'],['render_views.py','--check']]:
  p=subprocess.run([sys.executable,str(ROOT/'scripts'/cmd[0]),*cmd[1:]],capture_output=True,text=True)
  checks.append({'command':' '.join(cmd),'returncode':p.returncode})
  if p.returncode:errors.append({'command':cmd,'detail':p.stdout[-2500:]+p.stderr[-1000:]})
 try:
  from jsonschema import Draft202012Validator
  for p in list((ROOT/'interfaces').glob('*.schema.json'))+list((ROOT/'skills/chatgpt-ads/references').glob('*.schema.json')):Draft202012Validator.check_schema(json.loads(p.read_text()))
 except (ImportError,ValueError) as e:errors.append('schema validation unavailable or invalid: '+str(e))
 for p in (ROOT/'skills').glob('*/SKILL.md'):
  body=p.read_text()
  if not body.startswith('---\n') or not re.search(r'^name: [a-z0-9-]+$',body,re.M):errors.append('invalid frontmatter: '+str(p.relative_to(ROOT)))
  for ref in re.findall(r'`([^`\n]+\.(?:md|json|py))`',body):
   if ' ' not in ref and not (p.parent/ref).is_file():errors.append('missing skill path: '+ref)
 # Markdown relative links in active authored navigation; historical citations are excluded.
 paths=[p for base in ('brain','runtime','skills','docs') for p in (ROOT/base).rglob('*.md')]+[ROOT/n for n in ('README.md','SKILL.md','AGENTS.md','CLAUDE.md','CODEX.md','BUILD_STATUS.md')]
 paths += [ROOT/rel for rel,_ in entries if rel.suffix=='.md' and rel.parts[0]=='acceptance']
 for p in paths:
  if p.exists():
   for ref in re.findall(r'\]\(([^)]+)\)',p.read_text()):
    if ref.startswith(('https://','http://','#')):continue
    ref=ref.split('#')[0]
    if ref and not (p.parent/ref).exists():errors.append('broken link: '+str(p.relative_to(ROOT))+' -> '+ref)
 print(json.dumps({'status':'pass' if not errors else 'fail','skills':len(list((ROOT/'skills').glob('*/SKILL.md'))),'checks':checks,'errors':errors,'scope':'active local package validation; not source truth or account acceptance'},indent=2));return bool(errors)
if __name__=='__main__':sys.exit(main())

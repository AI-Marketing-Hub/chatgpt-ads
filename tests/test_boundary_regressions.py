import copy,hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from jsonschema import Draft202012Validator
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import package_release as pack,render_views as render,import_report as report
import test_packaging
class BoundaryRegressionTests(unittest.TestCase):
 def test_top_level_package_symlink_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'root';root.mkdir();test_packaging.PackageTests().fixture(root);(root/'brain/index.md').unlink();(root/'brain').rmdir();outside=Path(d)/'outside';outside.mkdir();(outside/'private.md').write_text('private sentinel');(root/'brain').symlink_to(outside)
   with self.assertRaisesRegex(ValueError,'symlink'):list(pack.selected(root))
 def test_report_uses_exact_snapshot_when_path_changes(self):
  original=R/'skills/chatgpt-ads/examples/normalized-demo.csv';data=original.read_bytes()
  context={'profile':'manual-normalized-v1','account_id':'synthetic-a','exported_at':'2026-09-10T00:00:00Z','source_sha256':hashlib.sha256(data).hexdigest(),'source_fields':list(report.an.FIELDS),'transformations':[],'mapping_review':'fixture',**report.an.read_normalized_bytes(data)[0].metadata}
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'input.csv';p.write_bytes(data)
   def read_then_replace(*args):p.write_bytes(b'changed invalid bytes');return data
   with patch.object(report,'read_regular',side_effect=read_then_replace):out=report.read_report(p,context,'synthetic-a')
   self.assertEqual(out['analysis'],report.an.analyze(report.an.read_normalized_bytes(data)))
 def test_bad_context_refuses(self):
  p=R/'skills/chatgpt-ads/examples/normalized-demo.csv'
  for context in [[],None,'text']:
   with self.assertRaises(ValueError):report.read_report(p,context,'synthetic-a')
 def test_blocked_requires_nonempty_reasons(self):
  validator=Draft202012Validator(json.loads((R/'skills/chatgpt-ads/references/result.schema.json').read_text()))
  x={'status':'blocked','workflow':'operate','as_of':'2026-09-10','findings':[],'missing_inputs':[],'actions':[],'live_execution':'not_performed'}
  self.assertTrue(list(validator.iter_errors(x)));x['blockers']=[];self.assertTrue(list(validator.iter_errors(x)))
 def render_root(self,root):
  (root/'references').mkdir();(root/'skills/chatgpt-ads/references').mkdir(parents=True)
  (root/'references/source-ledger.json').write_text(json.dumps({'sources':[{'id':'s','title':'Example','url':'https://example.com','retrieved':None}]}))
  (root/'references/claims.json').write_text(json.dumps({'claims':[{'id':'c','lane':'platform','claim':'Example','source_ids':['s']}]}))
  (root/'references/contradictions.json').write_text('{"contradictions":[]}')
 def test_render_unknown_date_and_symlink_output(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.render_root(root);self.assertIn('retrieved unknown',render.views(root)['skills/chatgpt-ads/references/platform-findings.md'])
   victim=root/'victim.md';victim.write_text('keep');target=root/'skills/chatgpt-ads/references/platform-findings.md';target.symlink_to(victim)
   with self.assertRaisesRegex(ValueError,'symlink'):render.render(root)
   self.assertEqual(victim.read_text(),'keep')
 def test_render_registry_drift_is_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.render_root(root);original=render.knowledge_core._transaction_commit
   def mutate_then_commit(*args,**kwargs):
    (root/'references/claims.json').write_text('{"claims":[]}')
    return original(*args,**kwargs)
   with patch.object(render.knowledge_core,'_transaction_commit',side_effect=mutate_then_commit),self.assertRaisesRegex(ValueError,'guarded'):
    render.render(root)
   self.assertFalse((root/'skills/chatgpt-ads/references/platform-findings.md').exists())
 def test_render_mid_commit_failure_rolls_back(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.render_root(root)
   expected=render.views(root)
   for name in expected:(root/name).write_text('before')
   original=render.knowledge_core.replace_regular;count=0
   def fail(src,dst,**kwargs):
    nonlocal count
    count+=1
    if count==2:raise OSError('synthetic interrupted write')
    return original(src,dst,**kwargs)
   with patch.object(render.knowledge_core,'replace_regular',side_effect=fail),self.assertRaises(render.knowledge_core.KnowledgeCoreError):render.render(root)
   for name in expected:self.assertEqual((root/name).read_text(),'before')
if __name__=='__main__':unittest.main()

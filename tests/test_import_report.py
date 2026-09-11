import copy,hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('report',ROOT/'scripts/import_report.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ReportTests(unittest.TestCase):
 def setUp(self):
  self.path=ROOT/'skills/chatgpt-ads/examples/normalized-demo.csv'
  self.context={'profile':'manual-normalized-v1','account_id':'synthetic-a','exported_at':'2026-09-10T00:00:00Z','source_sha256':hashlib.sha256(self.path.read_bytes()).hexdigest(),'source_fields':list(m.an.FIELDS),'transformations':[],'mapping_review':'synthetic test fixture only',**m.an.read_normalized_csv(self.path)[0].metadata}
 def test_valid_manual_stays_not_native(self):
  self.assertFalse(m.read_report(self.path,self.context,'synthetic-a')['native_mapping_verified'])
 def test_wrong_account(self):
  with self.assertRaisesRegex(ValueError,'wrong account'):m.read_report(self.path,self.context,'synthetic-b')
 def test_native_refuses_before_read(self):
  self.context['profile']='chatgpt-native-v1'
  with self.assertRaisesRegex(ValueError,'native profile unavailable'):m.read_report(Path('nonexistent'),self.context,'synthetic-a')
 def test_context_attribution_and_currency(self):
  for field in ('attribution_window','currency','granularity','timezone','date_start','conversion_definition'):
   c=copy.deepcopy(self.context);c[field]='different'
   with self.subTest(field=field),self.assertRaisesRegex(ValueError,'context mismatch'):m.read_report(self.path,c,'synthetic-a')
 def test_hash_and_review(self):
  c=copy.deepcopy(self.context);c['source_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'hash mismatch'):m.read_report(self.path,c,'synthetic-a')
  c=copy.deepcopy(self.context);c['mapping_review']=''
  with self.assertRaisesRegex(ValueError,'review required'):m.read_report(self.path,c,'synthetic-a')
 def test_symlink_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'input.csv';p.symlink_to(self.path)
   with self.assertRaisesRegex(ValueError,'regular input'):m.read_report(p,self.context,'synthetic-a')
if __name__=='__main__':unittest.main()

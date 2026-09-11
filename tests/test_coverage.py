import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CoverageTests(unittest.TestCase):
 def test_all_topics_resolve_evidence_and_procedure(self):
  data=json.loads((ROOT/'references/coverage.json').read_text());claims={c['id'] for c in json.loads((ROOT/'references/claims.json').read_text())['claims']};sources={s['id'] for s in json.loads((ROOT/'references/source-ledger.json').read_text())['sources']}
  self.assertEqual(len(data['areas']),13)
  self.assertEqual(len({a['id'] for a in data['areas']}),13)
  for a in data['areas']:
   with self.subTest(area=a['id']):
    self.assertTrue((ROOT/a['note']).is_file());self.assertTrue((ROOT/a['skill']).is_file())
    self.assertTrue(set(a['claim_ids'])<=claims);self.assertTrue(set(a['source_ids'])<=sources)
    self.assertTrue(a['limitations']);self.assertTrue(a['tests'])
    for t in a['tests']:self.assertTrue((ROOT/t).is_file())
 def test_no_claimed_account_acceptance(self):
  cap=json.loads((ROOT/'references/capabilities.json').read_text());self.assertFalse(cap['account_verified']);self.assertFalse(cap['live_action_verified'])
if __name__=='__main__':unittest.main()

import json,unittest
from pathlib import Path
from jsonschema import Draft202012Validator
R=Path(__file__).resolve().parents[1]
class ResultContractTests(unittest.TestCase):
 def test_workflow_failure_states_are_expressible(self):
  v=Draft202012Validator(json.loads((R/'skills/chatgpt-ads/references/result.schema.json').read_text()))
  for status in ['no_data','capability_unavailable','needs_approval','needs_reconciliation','blocked']:
   x={'status':status,'workflow':'operate','as_of':'2026-09-10','findings':[],'missing_inputs':[],'actions':[],'live_execution':'not_performed','blockers':[{'code':'wrong_account','detail':'observed B; approved A'},{'code':'uncertain_save','detail':'reconcile before retry'}]}
   self.assertEqual(list(v.iter_errors(x)),[])
   x['live_execution']='performed';self.assertTrue(list(v.iter_errors(x)))
if __name__=='__main__':unittest.main()

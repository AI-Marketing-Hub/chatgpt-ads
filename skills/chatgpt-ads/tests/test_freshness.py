import importlib.util
from datetime import date
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/'scripts/check_sources.py'
spec=importlib.util.spec_from_file_location('source_freshness',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class FreshnessTests(unittest.TestCase):
    def test_fresh_expired_unknown_and_invalid_dates(self):
        sources=[{'id':'test','retrieved':'2026-09-10','refresh_due':'2026-09-17'}]
        self.assertEqual(module.check(sources,['test'],date(2026,9,17))['status'],'pass')
        self.assertEqual(module.check(sources,['test'],date(2026,9,18))['status'],'blocked')
        self.assertEqual(module.check(sources,['missing'],date(2026,9,10))['status'],'blocked')
        self.assertEqual(module.check(sources,[],date(2026,9,10))['status'],'blocked')
        self.assertEqual(module.check(sources,['test'],date(2026,9,9))['status'],'blocked')
        sources[0]['refresh_due']='invalid'
        self.assertEqual(module.check(sources,['test'])['status'],'blocked')
if __name__=='__main__':unittest.main()

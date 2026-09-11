"""Exact-action regressions for observed automation and draft changes."""
import copy
import unittest
from test_browser_guard import records, NOW
from scripts.check_browser_action import check_browser_action
from scripts.operating_core import OperatingCoreError, sha256_canonical


def bind(plan, reviewed, observation):
    plan['action']['campaign_plan_sha256'] = sha256_canonical(reviewed)
    plan['approval']['approved_action_sha256'] = sha256_canonical(plan['action'])
    decision = {k:v for k,v in plan['approval'].items() if k != 'decision_sha256'}
    plan['approval']['decision_sha256'] = sha256_canonical(decision)
    observation['observed_settings'] = copy.deepcopy(plan['action']['before'])
    observation['proposed_settings'] = copy.deepcopy(plan['action']['after'])


class LaunchDefaultsTests(unittest.TestCase):
    def test_changed_personalization_invalidates_exact_batch(self):
        plan, reviewed, observation = records()
        plan['action']['before']['local_text_personalization'] = True
        plan['action']['after']['local_text_personalization'] = False
        reviewed['configuration']['approved_generated_changes'] = 'none'
        bind(plan, reviewed, observation)
        self.assertTrue(check_browser_action(plan, reviewed, observation, now=NOW)['eligible'])
        observation['proposed_settings']['local_text_personalization'] = True
        with self.assertRaisesRegex(OperatingCoreError, 'proposed settings'):
            check_browser_action(plan, reviewed, observation, now=NOW)

    def test_new_draft_requires_reconciliation_of_before_state(self):
        plan, reviewed, observation = records()
        plan['action']['before']['local_existing_draft_ids'] = []
        bind(plan, reviewed, observation)
        observation['observed_settings']['local_existing_draft_ids'] = ['synthetic-draft']
        with self.assertRaisesRegex(OperatingCoreError, 'observed settings'):
            check_browser_action(plan, reviewed, observation, now=NOW)

    def test_platform_limit_cannot_replace_approved_maximum(self):
        plan, reviewed, observation = records()
        observation['cost']['maximum_effect']['amount_micros'] = 10**15
        with self.assertRaisesRegex(OperatingCoreError, 'cost'):
            check_browser_action(plan, reviewed, observation, now=NOW)


if __name__ == '__main__':
    unittest.main()

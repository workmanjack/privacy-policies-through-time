from wayback_search import POLICY_DIR, REGEX_POLICY_DATE_LIST, get_update_date
from build_master_index import MASTER_CSV
import pandas as pd
import unittest
import os


REGEX_POLICY_DATE_LIST = [
    re.compile(r'amended as of (\w+ \d+)', flags=re.IGNORECASE),
    re.compile(r'amended as of (\w+\.* \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'Published: (\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'Last update: (\d+/\d+/\d+)', flags=re.IGNORECASE),
    re.compile(r'Last Revision: (\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'Last Revised: (\w+ \d+, \d+)'),
    re.compile(r'posted as of:? (\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'Last modified: (\w+ \d+, \d+)'),
    re.compile(r'(\d+-\d+-\d+) privacy policy'),
    re.compile(r'effective as of (\w+ \d+, \d+)'),
    re.compile(r'last modified on (\w+ \d+, \d+)'),
    re.compile(r'Effective Date: (\w+ \d+\w+ \d+)'),
    re.compile(r'Effective Date: (\w+ \d+, \d+)'),
    re.compile(r'Last Updated: *(\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'Last Updated: *(\d+ \w+ \d+)', flags=re.IGNORECASE),
    re.compile(r'Last revised on (\w+ \d+, \d+)'),
    re.compile(r'Revised: (\w+ \d+, \d+)'),
    re.compile(r'Revised ([^\.]*)'),
    re.compile(r'last updated in ([^\.]*)'),
    re.compile(r'last updated on (\w+ \d+\w*, \d+)', flags=re.IGNORECASE),
    re.compile(r'last updated on (.*) \('),
    re.compile(r'updated on\n? ?(\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'updated on ([^\.]*)', flags=re.IGNORECASE),
    re.compile(r'Privacy Policy dated (.*)\n'),
    re.compile(r'Last update:? (\w+ \d+, \d+)'),
    re.compile(r'LAST UPDATED (\w+ \d+, \d+)', flags=re.IGNORECASE),
    re.compile(r'LAST UPDATED (\w+,? \d+)', flags=re.IGNORECASE),
    re.compile(r'Updated: (.*)\n', flags=re.IGNORECASE),
    re.compile(r'Effective:? (.*)\n', flags=re.IGNORECASE),
    re.compile(r'Effective:? (\w+ \d+, \d+)', flags=re.IGNORECASE),
]


class TestUpdateDateRegex(unittest.TestCase):


    def test_policies(self):
        """
        Loop through all policies and test to see if we can pull out a date
        """
        df = pd.read_csv(MASTER_CSV)
        for path in df.policy_path:
            # build path
            path = os.path.join(POLICY_DIR, path)
            # get policy text
            policy = None
            with open(path, 'r', encoding='utf-8') as f:
                policy = f.read()
            # confirm we got it
            if not policy:
                print('WARNING: unable to read {}'.format(path))
            else:
                # commence test
                result = get_update_date(policy, regex_list=REGEX_POLICY_DATE_LIST)
                self.assertTrue(result is not None)

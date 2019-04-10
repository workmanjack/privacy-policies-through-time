from wayback_search import POLICY_DIR, REGEX_POLICY_DATE_LIST, REGEX_POLICY_DATE_MASTER, get_update_date
from build_master_index import MASTER_CSV
import pandas as pd
import unittest
import os
import re


POLICIES_MISSING_DATES = [
    'google/google-1999-09-20.txt',
    'google/google-2001-01-04.txt',
    'google/google-2004-07-01.txt',
    'google/google-2018-05-25.txt',
    'smud/smud-2016-06-22.txt'
]


REGEX_FILE_DATE = re.compile(r'(\d+-\d+-\d+)')


class TestUpdateDateRegex(unittest.TestCase):


    def test_policies(self):
        """
        Loop through all policies and test to see if we can pull out a date
        """
        # read master index to get policy paths
        df = pd.read_csv(MASTER_CSV)
        # remove policies that we know we can't read no matter how hard we try
        df = df[~df.policy_path.str.contains('|'.join(POLICIES_MISSING_DATES))]
        # loop through em
        for path in df.policy_path:
            print('testing {}'.format(path))
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
                result = get_update_date(policy, regex_list=REGEX_POLICY_DATE_MASTER)
                self.assertTrue(result is not None)
                # reuse get_update_date to pull date out of filename
                file_date = get_update_date(path, regex_list=[REGEX_FILE_DATE])
                # and now compare dates for extra fidelity
                self.assertEqual(result.year, file_date.year)
                self.assertEqual(result.month, file_date.month)
                self.assertEqual(result.day, file_date.day)

    def test_group_or(self):
        """
        """
        tests = [
            ('faeava Effective: November 2003 faeage', (11, 9, 2003)),
            ('faeava Effective: Nov. 2003 faeage', (11, 9, 2003)),
            ('faeava Effective: November, 2003 faeage', (11, 9, 2003)),
            ('ffeafe Effective: November 1, 2003 feage', (11, 1, 2003)),
            ('aabaev Effective: November 2 2003 feafeage', (11, 2, 2003)),
            ('faeava Effective: 3 November 2003 faeage', (11, 3, 2003)),
            ('faeava Effective: 3 November, 2003 faeage', (11, 3, 2003)),
            ('faeava Effective: Nov. 4 2003 faeage', (11, 4, 2003)),
            ('faeava Effective: 11/5/2003 faeage', (11, 5, 2003)),
            ('faeava Effective: 11-6-2003 faeage', (11, 6, 2003)),
            ('faeava Effective: Nov. 7th 2003 faeage', (11, 7, 2003)),
            ('faeava Effective: November 8th 2003 faeage', (11, 8, 2003)),
            ('faeava Effective: November 9th, 2003 faeage', (11, 9, 2003)),
        ]
        for test, answer in tests:
            print(test)
            d = get_update_date(test, REGEX_POLICY_DATE_LIST)
            print(d)
            self.assertTrue(d is not None)
            self.assertEqual(d.month, answer[0])
            self.assertEqual(d.day, answer[1])
            self.assertEqual(d.year, answer[2])

    def test_prefix_or(self):
        """
        """
        tests = [
            ('ffeafe Effective: November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Effective November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe effective November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe Updated: November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Updated November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe updated November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe Last Updated: November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Last updated: November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe last updated November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe updated on November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Updated on: November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Updated On November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe Last updated in November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Last updated on November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe last updated on November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe revised November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Revised November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Revised: November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe last revised on November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Last revised on: November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe Effective Date: November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe effective date: November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Effective date November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe amended as of November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Amended as of November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe Amended as of: November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe posted as of: November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe posted as of November 1, 2003 feage', (11, 1, 2003)),

            ('ffeafe last modified on: November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe last modified on November 1, 2003 feage', (11, 1, 2003)),
            ('ffeafe last modified: November 1, 2003 feage', (11, 1, 2003)),
        ]
        for test, answer in tests:
            print(test)
            d = get_update_date(test, REGEX_POLICY_DATE_LIST)
            print(d)
            self.assertTrue(d is not None)
            self.assertEqual(d.month, answer[0])
            self.assertEqual(d.day, answer[1])
            self.assertEqual(d.year, answer[2])

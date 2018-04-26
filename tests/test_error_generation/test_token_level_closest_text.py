import unittest
import pandas as pd
import numpy as np

from common.read_data.read_data import read_all_c_records
from error_generation.find_closest_group_data.token_level_closest_text import init_c_code, recovery_code
from common.util import group_df_to_grouped_list
from error_generation.find_closest_group_data.closest_group_producer import find_closest_group


class TestToken_Level_ClosestText(unittest.TestCase):

    def setUp(self):
        self.data_df = read_all_c_records()
        self.data_df = self.data_df[self.data_df['code'].map(lambda x: x is not '')]

        self.data_df = init_c_code(self.data_df)
        print(len(self.data_df.index))
        self.group_list = group_df_to_grouped_list(self.data_df, 'problem_user_id')
        self.group_list = list(filter(lambda x: self.check_group_has_both(x), self.group_list))


    def check_group_has_both(self, df):
        hasAC = False
        hasError = False

        res = df['status'].map(lambda x: 1 if x == 1 else 0)
        if np.sum(res) > 0:
            hasAC = True

        res = df['status'].map(lambda x: 1 if x == 7 else 0)
        if np.sum(res) > 0:
            hasError = True
        return hasAC & hasError

    def test_group_df_to_grouped_list(self):
        group_list = group_df_to_grouped_list(self.data_df, 'problem_user_id')
        group_list = list(filter(lambda x: self.check_group_has_both(x), group_list))
        print(group_list[0])
        print(len(group_list))
        self.assertIsInstance(group_list[0], pd.DataFrame)

    def recovery_tokenize(self, one, ac_df):
        ac_id = one['similar_id']
        ac_tokenize = ac_df[ac_df['id'].map(lambda x: x == ac_id)].iloc[0]['tokenize']
        error_tokenize = recovery_code(ac_tokenize, one['action_list'])
        target_tokenize = one['tokenize']
        self.assertEqual(len(error_tokenize), len(target_tokenize))
        for err, target in zip(error_tokenize, target_tokenize):
            self.assertEqual(err.value, target.value)

    def test_find_closest_group(self):
        error_df, ac_df = find_closest_group(self.group_list[0])
        error_df = error_df[error_df['similar_code'].map(lambda x: x is not '')]
        error_df.apply(self.recovery_tokenize, axis=1, raw=True, ac_df=ac_df)
        print(error_df)
        print(ac_df)

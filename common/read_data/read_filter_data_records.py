from common.read_data.read_data import read_train_data_effect_all_c_error_records, read_train_data_all_c_error_records, read_compile_success_c_records
from common.filter_test_set import filter_distinct_problem_user_id
from common.util import disk_cache
from common.constants import CACHE_DATA_PATH


def read_distinct_problem_user_c_records():
    data_df = read_train_data_all_c_error_records()
    print('origin data size: ', len(data_df))
    data_df = data_df[data_df['distance'].map(lambda x: x != -1)]
    print('after filter distance!=-1 size: ', len(data_df))
    data_df = filter_distinct_problem_user_id(data_df)
    print('after filter distinct problem user size: ', len(data_df))
    return data_df


@disk_cache(basename='read_distinct_problem_user_compile_success_c_records', directory=CACHE_DATA_PATH)
def read_distinct_problem_user_compile_success_c_records():
    data_df = read_compile_success_c_records()
    print('origin data size: ', len(data_df))
    data_df = data_df[data_df['gcc_compile_result'].map(lambda x: x == 1)]
    print('after filter success records: {}'.format(len(data_df)))
    data_df = filter_distinct_problem_user_id(data_df)
    print('after filter distinct problem user size: ', len(data_df))
    return data_df

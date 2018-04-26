from common.read_data.read_data import read_train_data_effect_all_c_error_records, read_train_data_all_c_error_records, \
    read_compile_success_c_records, read_fake_common_c_error_records, read_fake_random_c_error_records
from common.filter_test_set import filter_distinct_problem_user_id
from common.util import disk_cache
from common.constants import CACHE_DATA_PATH


@disk_cache(basename='read_distinct_problem_user_c_records', directory=CACHE_DATA_PATH)
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


def read_distinct_problem_user_ac_c_records_filter_error_code():
    ac_df = read_distinct_problem_user_compile_success_c_records()
    print('total distinct ac c records: {}'.format(len(ac_df)))
    error_df = read_distinct_problem_user_c_records()
    print('total error c records: {}'.format(len(error_df)))
    ac_df = ac_df[~ac_df['user_id'].isin(error_df['user_id'])]
    # ac_df = ac_df[ac_df['user_id'].map(lambda x: x not in error_df['user_id'])]
    print('ac df length after filter user_id in error df: {}'.format(len(ac_df)))
    return ac_df


@disk_cache(basename='read_distinct_problem_user_fake_c_random_records', directory=CACHE_DATA_PATH)
def read_distinct_problem_user_fake_c_random_records():
    data_df = read_fake_random_c_error_records()
    print('origin data size: ', len(data_df))
    data_df = data_df[data_df['distance'].map(lambda x: 0 < x < 10)]
    print('after filter distance length between 0 and 10: ', len(data_df))
    data_df = filter_distinct_problem_user_id(data_df)
    print('after filter distinct problem user size: ', len(data_df))
    return data_df


@disk_cache(basename='read_distinct_problem_user_fake_c_common_records', directory=CACHE_DATA_PATH)
def read_distinct_problem_user_fake_c_common_records():
    data_df = read_fake_common_c_error_records()
    print('origin data size: ', len(data_df))
    data_df = data_df[data_df['distance'].map(lambda x: 0 < x < 10)]
    print('after filter distance length between 0 and 10: ', len(data_df))
    data_df = filter_distinct_problem_user_id(data_df)
    print('after filter distinct problem user size: ', len(data_df))
    return data_df


if __name__ == '__main__':
    df = read_distinct_problem_user_ac_c_records_filter_error_code()

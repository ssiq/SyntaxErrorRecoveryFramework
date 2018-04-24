from common.read_data.read_filter_data_records import read_distinct_problem_user_compile_success_c_records



def filter_frac(data_df, frac):
    user_count = len(data_df.groupby('user_id').size())
    print('user_count: {}'.format(user_count))
    user_id_list = data_df['user_id'].sample(int(user_count * frac)).tolist()
    print('user_id_list: {}'.format(len(user_id_list)))
    split_df = data_df[data_df.apply(lambda x: x['user_id'] in user_id_list, axis=1, raw=True)]
    print('split_df: {}'.format(len(split_df)))
    # drop_df = data_df[data_df.apply(lambda x: x['user_id'] in user_id_list, axis=1, raw=True)]
    main_df = data_df.drop(split_df.index)
    print('main_df: {}'.format(len(main_df)))
    return main_df, split_df


def read_distinct_problem_user_ac_c99_code_dataset():
    data_df = read_distinct_problem_user_compile_success_c_records()

    main_df, test_df = filter_frac(data_df, 0.1)
    train_df, vaild_df = filter_frac(main_df, 0.1)
    print('train df size: {}, valid df size: {}, test df size: {}'.format(len(train_df), len(vaild_df), len(test_df)))
    return train_df, vaild_df, test_df


if __name__ == '__main__':
    # data_df = read_distinct_problem_user_compile_success_c_records()
    # print('all data df', len(data_df))
    # main_df, split_df = filter_frac(data_df, 0.1)
    # print('train_df length: {}, split_df length: {}'.format(len(main_df), len(split_df)))
    read_distinct_problem_user_ac_c99_code_dataset()

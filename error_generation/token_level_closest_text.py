from common.constants import TRAIN_DATA_DBPATH, ACTUAL_C_ERROR_RECORDS, CACHE_DATA_PATH
from common.action_constants import ActionType
from common.util import compile_c_code_by_gcc, parse_c_code_by_pycparser, init_pycparser, tokenize_by_clex, parallel_map, \
    init_code, check_ascii_character, disk_cache
from error_recovery.buffered_clex import BufferedCLex
from error_generation.levenshtenin_token_level import levenshtenin_distance
from error_generation.produce_actions import cal_action_list
from common.read_data.read_data import read_all_c_records
from database.database_util import create_table, insert_items
from common.util import tokenize_error_count

import pandas as pd
import re
import json
import numpy as np
import multiprocessing
import sys

def generate_equal_fn(token_value_fn=lambda x:x):
    def equal_fn(x, y):
        x_val = token_value_fn(x)
        y_val = token_value_fn(y)
        return x_val == y_val
    return equal_fn


def get_token_value(x):
    val = x.value
    if isinstance(val, list):
        val = ''.join(val)
    return val

a_tokenize_error_count = 0
ac_df_length_error = 0
distance_series_error = 0

def find_closest_token_text(one, ac_df):
    global a_tokenize_error_count, ac_df_length_error, distance_series_error
    equal_fn = generate_equal_fn(get_token_value)
    a_tokenize = one['tokenize']
    a_code = one['code']
    ac_df = ac_df[ac_df['code'].map(lambda x: check_include_between_two_code(a_code, x))]

    if a_tokenize is None or len(ac_df) == 0:
        one['similar_code'] = ''
        one['action_list'] = []
        one['distance'] = -1
        one['similar_id'] = ''
        # print('a_tokenize is None {}, and len ac_df is {}'.format(type(a_tokenize), len(ac_df)))
        if a_tokenize is None:
            a_tokenize_error_count += 1
        elif len(ac_df) == 0:
            ac_df_length_error += 1
        return one
    cal_distance_fn = lambda x: levenshtenin_distance(a_tokenize, x, equal_fn=equal_fn)[0]
    distance_series = ac_df['tokenize'].map(cal_distance_fn)
    distance_series = distance_series[distance_series.map(lambda x: x >= 0)]
    if len(distance_series.index) <= 0:
        one['similar_code'] = ''
        one['action_list'] = []
        one['distance'] = -1
        one['similar_id'] = ''
        # print('distance series len is {}'.format(len(distance_series)))
        distance_series_error += 1
        return one
    min_id = distance_series.idxmin()
    min_value = distance_series.loc[min_id]

    matrix = levenshtenin_distance(a_tokenize, ac_df['tokenize'].loc[min_id], equal_fn=equal_fn)[1]
    b_tokenize = ac_df['tokenize'].loc[min_id]
    action_list = cal_action_list(matrix, a_tokenize, b_tokenize, left_move_action, top_move_action, left_top_move_action, equal_fn, get_token_value)
    one['distance'] = min_value
    one['similar_code'] = ac_df['code'].loc[min_id]
    one['action_list'] = action_list
    one['similar_id'] = ac_df['id'].loc[min_id]
    return one


def check_group_has_both(df):
    hasAC = False
    hasError = False

    res = df['status'].map(lambda x: 1 if x == 1 else 0)
    if np.sum(res) > 0:
        hasAC = True

    res = df['status'].map(lambda x: 1 if x == 7 else 0)
    if np.sum(res) > 0:
        hasError = True
    return hasAC & hasError


count = 0
def find_closest_group(one_group: pd.DataFrame):
    sys.setrecursionlimit(5000)
    global count, a_tokenize_error_count, ac_df_length_error, distance_series_error
    current = multiprocessing.current_process()
    if count % 1 == 0:
        print('iteration {} in process {} {}:tokenize_error_count: {}, a_tokenize_error_count: {}, '
              'ac_df_length_error: {}, distance_series_error: {}'.format(count, current.pid, current.name,
                                                                         tokenize_error_count, a_tokenize_error_count,
                                                                         ac_df_length_error, distance_series_error))
    count += 1
    # if not check_group_has_both(one_group):
    #     return None

    c_parser = init_pycparser(lexer=BufferedCLex)
    file_path = '/dev/shm/tmp_file_{}.c'.format(current.pid)
    one_group['gcc_compile_result'] = one_group['code'].apply(compile_c_code_by_gcc, file_path=file_path)
    one_group['pycparser_result'] = one_group['code'].apply(parse_c_code_by_pycparser, file_path=file_path, c_parser=c_parser, print_exception=False)
    one_group['code_without_include'] = one_group['code'].map(remove_include).map(lambda x: x.replace('\r', ''))
    one_group['tokenize'] = one_group['code_without_include'].apply(tokenize_by_clex, lexer=c_parser.clex)
    one_group = one_group[one_group['tokenize'].map(lambda x: x is not None)]

    ac_df = one_group[one_group['gcc_compile_result']]
    error_df = one_group[one_group['gcc_compile_result'].map(lambda x: not x)]

    error_df = error_df.apply(find_closest_token_text, axis=1, raw=True, ac_df=ac_df)
    # error_df = error_df[error_df['res'].map(lambda x: x is not None)]
    if 'tokenize' in error_df.columns.values.tolist():
        error_df = error_df.drop(['tokenize'], axis=1)
    if 'tokenize' in ac_df.columns.values.tolist():
        ac_df = ac_df.drop(['tokenize'], axis=1)
    return error_df, ac_df


def check_include_between_two_code(code1, code2):
    names1 = extract_include_from_code(code1)
    names2 = extract_include_from_code(code2)
    return equal_include(names1, names2)


def extract_include_from_code(code):
    includes = extract_include(code)
    include_names = [extract_include_name(inc) for inc in includes]
    return include_names


def remove_include(code):
    lines = code.split('\n')
    pattern = re.compile('#include *<(.*)>|#include *"(.*)"')
    lines_without_include = list(filter(lambda line: pattern.match(line) is None, lines))
    return '\n'.join(lines_without_include)


def equal_include(names1, names2):
    if len(names1) != len(names2):
        return False
    for inc1, inc2 in zip(names1, names2):
        if inc1 != inc2:
            return False
    return True


def extract_include(code):
    lines = code.split('\n')
    lines_without_include = list(filter(lambda line: 'include' not in line, lines))
    pattern = re.compile('#include *<(.*)>|#include *"(.*)"')
    lines = map(str.strip, lines)
    include_lines = list(filter(lambda line: pattern.match(line) is not None, lines))
    return include_lines


def extract_include_name(include):
    include = include.strip()
    m = re.match('#include *<(.*)>', include)
    if m:
        return m.group(1)
    m = re.match('#include *"(.*)"', include)
    if m:
        return m.group(1)
    return None


def left_move_action(i, j, a_token, b_token, value_fn=lambda x: x):
    action = {'act_type': ActionType.DELETE, 'from_char': value_fn(b_token), 'to_char': '', 'token_pos': j-1}
    return action


def top_move_action(i, j, a_token, b_token, value_fn=lambda x: x):
    action = {'act_type': ActionType.INSERT_BEFORE, 'from_char': '', 'to_char': value_fn(a_token), 'token_pos': j}
    return action


def left_top_move_action(matrix, i, j, a_token, b_token, value_fn=lambda x: x):
    if matrix[i][j] == matrix[i-1][j-1]:
        return None
    action = {'act_type': ActionType.CHANGE, 'from_char': value_fn(b_token), 'to_char': value_fn(a_token), 'token_pos': j-1}
    return action


def recovery_code(tokens, action_list):
    # action_list.reverse()

    for act in action_list:
        act_type = act['act_type']
        pos = act['token_pos']
        from_char = act['from_char']
        to_char = act['to_char']
        if act_type == ActionType.INSERT_BEFORE:
            tokens = tokens[0:pos] + [to_char] + tokens[pos:]
        elif act_type == ActionType.DELETE:
            tokens = tokens[0:pos] + tokens[pos+1:]
        elif act_type == ActionType.CHANGE:
            tokens = tokens[0:pos] + [to_char] + tokens[pos+1:]
        else:
            print('action type error: {}'.format(act_type))
    return tokens


def create_id(one):
    user = one['user_id']
    problem = one['problem_name']
    return problem + '_' + user


def deal_action_type(action_list):
    for action in action_list:
        action['act_type'] = action['act_type'].value
    return action_list


def transform_data_list(one):
    item = []
    item += [one['id']]
    item += [one['submit_url']]
    item += [one['problem_id']]
    item += [one['user_id']]
    item += [one['problem_user_id']]
    item += [one['code']]
    item += [1 if one['gcc_compile_result'] else 0]
    item += [1 if one['pycparser_result'] else 0]
    item += [one['similar_code']] if not one['gcc_compile_result'] else ['']
    action_list = deal_action_type(one['action_list'])
    item += [json.dumps(action_list)] if not one['gcc_compile_result'] else ['']
    item += [int(one['distance'])] if not one['gcc_compile_result'] else [-1]
    return item


def group_df_to_grouped_list(data_df, groupby_key):
    grouped = data_df.groupby(groupby_key)
    group_list = []
    for name, group in grouped:
        group_list += [group]
    return group_list


@disk_cache(basename='init_c_code', directory=CACHE_DATA_PATH)
def init_c_code(data_df):
    data_df['problem_user_id'] = data_df.apply(create_id, axis=1, raw=True)
    data_df['code'] = data_df['code'].map(init_code)
    print('data length before check ascii: {}'.format(len(data_df)))
    data_df = data_df[data_df['code'].map(check_ascii_character)]
    print('data length after check ascii: {}'.format(len(data_df)))
    data_df = data_df[data_df['code'].map(lambda x: x != '')]
    return data_df


def save_train_data(error_df_list, ac_df_list):
    create_table(TRAIN_DATA_DBPATH, ACTUAL_C_ERROR_RECORDS)

    def trans(error_df):
        res = [transform_data_list(row) for index, row in error_df.iterrows()]
        return res

    error_items_list = [trans(error_df) for error_df in error_df_list]
    for error_items in error_items_list:
        insert_items(TRAIN_DATA_DBPATH, ACTUAL_C_ERROR_RECORDS, error_items)
    # ac_items_list = [list(ac_df.apply(transform_data_list, raw=True, axis=1)) for ac_df in ac_df_list]
    # for ac_items in ac_items_list:
    #     insert_items(TRAIN_DATA_DBPATH, ACTUAL_C_ERROR_RECORDS, ac_items)


if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    data_df = read_all_c_records()
    # data_df = data_df.sample(100000)
    print('finish read code: {}'.format(len(data_df.index)))
    data_df = init_c_code(data_df)
    print('finish init code: {}'.format(len(data_df.index)))
    # data_df = data_df.sample(10000)

    group_list = group_df_to_grouped_list(data_df, 'problem_user_id')
    print('group list length: {}'.format(len(group_list)))
    group_list = list(filter(check_group_has_both, group_list))
    print('after filter both group list length: {}'.format(len(group_list)))
    res = list(parallel_map(8, find_closest_group, group_list))
    # res = [find_closest_group(group) for group in group_list]
    res = list(filter(lambda x: x is not None, res))

    error_df_list, ac_df_list = list(zip(*res))

    total = 0
    for df in error_df_list:
        total += len(df)
    print('final train code: {}'.format(total))
    # save records
    save_train_data(error_df_list, ac_df_list)







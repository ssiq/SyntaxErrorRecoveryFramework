from common.constants import verdict
from common.action_constants import ActionType
from common.util import compile_c_code_by_gcc, parse_c_code_by_pycparser, init_pycparser, tokenize_by_clex, parallel_map
from error_recovery.buffered_clex import BufferedCLex
from error_generation.levenshtenin_token_level import levenshtenin_distance
from common.read_data.read_data import read_all_c_records

import pandas as pd
import re

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


def find_closest_token_text(one, ac_df):
    equal_fn = generate_equal_fn(get_token_value)
    a_tokenize = one['tokenize']
    cal_distance_fn = lambda x: levenshtenin_distance(a_tokenize, x, equal_fn=equal_fn)[0]
    distance_series = ac_df['tokenize'].map(cal_distance_fn)
    if len(distance_series.index) <= 0:
        one['similar_code'] = ''
        one['action_list'] = []
        one['distance'] = -1
        return one
    min_id = distance_series.idxmin()
    min_value = distance_series.loc[min_id]

    matrix = levenshtenin_distance(a_tokenize, ac_df['tokenize'].loc[min_id], equal_fn=equal_fn)[1]
    b_tokenize = ac_df['tokenize'].loc[min_id]
    action_list = ac_df(matrix, a_tokenize, b_tokenize, equal_fn, get_token_value)
    one['distance'] = min_value
    one['similar_code'] = ac_df['code'].loc[min_id]
    one['action_list'] = action_list
    return one


def find_closest_group(one_group:pd.DataFrame):
    c_parser = init_pycparser(lexer=BufferedCLex)
    file_path = 'tmp_file.c'
    one_group['gcc_compile_result'] = one_group['code'].apply(compile_c_code_by_gcc, file_path=file_path)
    one_group['pycparser_result'] = one_group['code'].apply(parse_c_code_by_pycparser, file_path=file_path, c_parser=c_parser, print_exception=False)

    one_group['code_without_include'] = one_group['code'].map(remove_include)
    one_group['tokenize'] = one_group['code_without_include'].apply(tokenize_by_clex, lexer=c_parser.clex)

    ac_df = one_group[one_group['gcc_compile_result']]
    error_df = one_group[one_group['gcc_compile_result'].map(lambda x: not x)]

    error_df = error_df.apply(find_closest_token_text, axis=1, raw=True, ac_df=ac_df)
    error_df = error_df[error_df['res'].map(lambda x: x is not None)]

    return error_df


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
    lines = lines.map(str.strip)
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


if __name__ == '__main__':
    data_df = read_all_c_records()
    data_df['identify'] = data_df.apply(create_id)

    grouped = data_df.groupby('identify')
    group_list = []
    for name, group in grouped:
        group_list += [group]
    res = list(parallel_map(8, find_closest_group, group_list))
    # save res





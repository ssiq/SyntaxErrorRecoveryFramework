import re

from common.util import write_code_to_file, preprocess, tokenize_by_clex


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


def replace_include_with_blank(code):
    lines = code.split('\n')
    pattern = re.compile('#include *<(.*)>|#include *"(.*)"')
    lines_without_include = [line if pattern.match(line) is None else '' for line in lines]
    return '\n'.join(lines_without_include)


def analyse_include_line_no(code, include_lines):
    lines = code.split('\n')
    include_line_nos = [match_one_include_line_no(lines, include_line) for include_line in include_lines]
    return include_line_nos


def match_one_include_line_no(lines, include_line):
    for i in range(len(lines)):
        if lines[i] == include_line:
            return i
    print('match one include line no error. lines: {}, include_line:{}'.format(lines, include_line))
    return None


def equal_include(names1, names2):
    if len(names1) != len(names2):
        return False
    for inc1, inc2 in zip(names1, names2):
        if inc1 != inc2:
            return False
    return True


def extract_include(code):
    lines = code.split('\n')
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


def calculate_include_preprocess_token_length(include_name, file_path, clex, is_system=True, add_include=True, user_header_path=[]):
    if is_system:
        line = '#include<{}>'.format(include_name)
    else:
        line = '#include"{}"'.format(include_name)
    write_code_to_file(line, file_path)
    text = preprocess(file_path, user_header_path)
    tokens = tokenize_by_clex(text, clex)
    return len(tokens)
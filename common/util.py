import collections
import types
import os
from subprocess import Popen, PIPE
import typing
import shutil
import pickle
import errno
import functools
import pandas as pd
import more_itertools
import hashlib
from multiprocessing import Pool
import re
import random

import config

from common.action_constants import ActionType
from pycparser.pycparser.c_parser import CParser
from pycparser.pycparser.c_lexer import CLexer
from common.new_tokenizer import tokenize


def maintain_function_co_firstlineno(ori_fn):
    """
    This decorator is used to make the decorated function's co_firstlineno the same as the ori_fn
    """

    def wrapper(fn):
        wrapper_code = fn.__code__
        fn.__code__ = types.CodeType(
            wrapper_code.co_argcount,
            wrapper_code.co_kwonlyargcount,
            wrapper_code.co_nlocals,
            wrapper_code.co_stacksize,
            wrapper_code.co_flags,
            wrapper_code.co_code,
            wrapper_code.co_consts,
            wrapper_code.co_names,
            wrapper_code.co_varnames,
            wrapper_code.co_filename,
            wrapper_code.co_name,
            ori_fn.__code__.co_firstlineno,
            wrapper_code.co_lnotab,
            wrapper_code.co_freevars,
            wrapper_code.co_cellvars
        )

        return fn

    return wrapper


def write_code(code, file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    f = open(file_path, 'w')
    f.write(code)
    f.flush()
    f.close()


def preprocess_file(filename:str, cpp_path: str='cpp', cpp_args: typing.Union[str, typing.List[str]]='') -> str:
    """ Preprocess a file using cpp.

        filename:
            Name of the file you want to preprocess.

        cpp_path:
        cpp_args:
            Refer to the documentation of parse_file for the meaning of these
            arguments.

        When successful, returns the preprocessed file's contents.
        Errors from cpp will be printed out.
    """
    path_list = [cpp_path]
    if isinstance(cpp_args, list):
        path_list += cpp_args
    elif cpp_args != '':
        path_list += [cpp_args]
    path_list += [filename]

    try:
        # Note the use of universal_newlines to treat all newlines
        # as \n for Python's purpose
        #
        pipe = Popen(   path_list,
                        stdout=PIPE,
                        universal_newlines=True)
        text = pipe.communicate()[0]
    except OSError as e:
        raise RuntimeError("Unable to invoke 'cpp'.  " +
            'Make sure its path was passed correctly\n' +
            ('Original error: %s' % e))

    return text


def preprocess(file_path: str, user_header_paths: typing.List[str]=list()) -> str:
    cpp_args = ['-I{}'.format(config.fake_system_header_path)]
    for s in user_header_paths:
        cpp_args.append('-I{}'.format(s))
    # print()
    # print(cpp_args)
    return preprocess_file(file_path, cpp_args=cpp_args)


def make_dir(*path: str) -> None:
    """
    This method will recursively create the directory
    :param path: a variable length parameter
    :return:
    """
    path = os.path.join(*path)

    if not path:
        return

    if os.path.exists(path):
        if not os.path.isdir(path):
            raise ValueError("The path {} already exits but it is not a directory".format(path))
        return

    base, _ = os.path.split(path)
    make_dir(base)
    os.mkdir(path)


def remove_content_in_dir(path: str) -> None:
    for c in os.listdir(path):
        c = os.path.join(path, c)
        if os.path.isdir(c):
            shutil.rmtree(c)
        else:
            os.remove(c)


def build_code_string_from_lex_tokens(tokens):
    """
    This function build the original code string from the token iterator
    :param tokens: Token iterator
    :return: code string
    """
    lex_tokens = iter(tokens)
    code_re = ""
    lino_pre = 1
    lexpos_pre = 0
    lexpos_temp = 0
    lenth_v = 0
    for token in lex_tokens:
        lino_temp = token.lineno
        if (lino_temp != lino_pre):
            code_re = code_re + "\n"*(lino_temp - lino_pre)
            lenth_v = lino_temp - lino_pre + 1
        else:
            code_re = code_re
        lino_pre = token.lineno
        lexpos_temp = token.lexpos
        code_re = code_re + " " * (lexpos_temp - lexpos_pre - lenth_v)
        code_re = code_re + str(token.value)
        lexpos_pre = lexpos_temp
        lenth_v = len(str(token.value))

    print(code_re)
    return code_re


def modify_lex_tokens_offset(ori_tokens: list, action_type, position, token=None):
    """
    Modify the lex token list according to action object. This function will also modify offset of tokens. Lineno will
    not change.
    Action: {action_type, action_position, action_value}
    :param ori_tokens:
    :param action_type:
    :param position:
    :param token
    :return:
    """
    if isinstance(action_type, int):
        action_type = ActionType(action_type)

    if position < 0 or (action_type == ActionType.INSERT_BEFORE and position > len(ori_tokens)) \
            or (action_type != ActionType.INSERT_BEFORE and position >= len(ori_tokens)):
        raise Exception('action position error. ori_tokens len: {}, action_type: {}, position: {}\n ' +
                        'token.type: {}, token.value: {}'.format(len(ori_tokens), action_type, position,
                                                                 token.type, token.value))

    new_tokens = ori_tokens
    if isinstance(new_tokens, tuple):
        new_tokens = list(new_tokens)

    if action_type is not ActionType.INSERT_BEFORE and action_type is not ActionType.INSERT_AFTER:
        new_tokens = new_tokens[:position] + new_tokens[position+1:]
        bias = 0 - len(ori_tokens[position].value) + 1
        new_tokens = modify_bias(new_tokens, position, bias)

    if action_type is not ActionType.DELETE:
        token, token_index = set_token_position_info(new_tokens, action_type, position, token)
        new_tokens = new_tokens[:token_index] + [token] + new_tokens[token_index:]
        bias = len(token.value) + 2
        new_tokens = modify_bias(new_tokens, token_index + 1, bias)
    return new_tokens


def set_token_position_info(tokens, action_type, position, token):
    if (action_type is ActionType.INSERT_BEFORE or action_type is ActionType.CHANGE) and position == len(tokens):
        position -= 1
        action_type = ActionType.INSERT_AFTER
    if position < len(tokens) and action_type is not ActionType.INSERT_AFTER:
        according_token = tokens[position]
        token = set_token_line_pos_accroding_before(according_token, token)
    else:
        if action_type is ActionType.INSERT_BEFORE:
            position -= 1
        according_token = tokens[position]
        token = set_token_line_pos_accroding_after(according_token, token)
        position += 1
    return token, position


def set_token_line_pos_accroding_before(according_token, token):
    token.lineno = according_token.lineno
    token.lexpos = according_token.lexpos + 1
    return token


def set_token_line_pos_accroding_after(according_token, token):
    token.lineno = according_token.lineno
    token.lexpos = according_token.lexpos + len(according_token.value) + 1
    return token


def modify_bias(tokens, position, bias):
    for tok in tokens[position:]:
        tok.lexpos += bias
    return tokens


def compile_syntax_c_code_by_gcc(code, file_path):
    write_code_to_file(code, file_path)
    # res = os.system('gcc -fsyntax-only -pedantic-errors -std=gnu99 {} >/dev/null 2>/dev/null'.format(file_path))
    res = os.system('gcc -c -pedantic-errors -std=gnu99 {} >/dev/null 2>/dev/null'.format(file_path))
    if res == 0:
        return True
    return False


def compile_c_code_by_gcc(code, file_path):
    write_code_to_file(code, file_path)
    res = os.system('gcc -pedantic-errors -std=gnu99 {} >/dev/null 2>/dev/null'.format(file_path))
    # res = os.system('gcc -pedantic-errors -std=gnu99 {}'.format(file_path))
    if res == 0:
        return True
    return False


def compile_c_code_by_gcc_c89(code, file_path):
    write_code_to_file(code, file_path)
    res = os.system('gcc -pedantic-errors -std=gnu89 {} >/dev/null 2>/dev/null'.format(file_path))
    # res = os.system('gcc -pedantic-errors -std=gnu89 {}'.format(file_path))
    if res == 0:
        return True
    return False


def compile_cpp_code_by_gcc(code, file_path):
    write_code_to_file(code, file_path)
    # res = os.system('g++ -c -pedantic-errors -std=gnu99 {} >/dev/null 2>/dev/null'.format(file_path))
    res = os.system('g++ {} >/dev/null 2>/dev/null'.format(file_path))
    # res = os.system('g++ {}'.format(file_path))
    # print('g++ -I/usr/local/include -std=gnu++98 {}'.format(file_path))
    if res == 0:
        return True
    return False

def tokenize_cpp_code_by_new_tokenize(code, print_exception=False):
    try:
        if code.find('define') != -1 or code.find('defined') != -1 or code.find('undef') != -1 or \
                        code.find('pragma') != -1 or code.find('ifndef') != -1 or \
                        code.find('ifdef') != -1 or code.find('endif') != -1:
            return None
        tokens = tokenize(code)
        if len(tokens) > 2000:
            return None
        return tokens
    except Exception as e:
        if print_exception:
            print(e)
        return None


def write_code_to_file(code, file_path):
    file_path = os.path.abspath(file_path)
    ensure_file_path(file_path)
    f = open(file_path, 'w')
    f.write(code)
    f.flush()
    f.close()
    return file_path


def ensure_file_path(file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))


def parse_c_code_by_pycparser(code, file_path, c_parser=None, print_exception=True):
    if c_parser is None:
        c_parser = init_pycparser()
    write_code_to_file(code, file_path)
    preprocess_code = preprocess(file_path)
    preprocess_code = preprocess_code.replace('\r', '')
    try:
        root = c_parser.parse(preprocess_code)
    except Exception as e:
        if print_exception:
            print(e)
        return False
    return True


def init_pycparser(lexer=CLexer):
    c_parser = CParser()
    c_parser.build(lexer=lexer)
    return c_parser


def tokenize_by_clex_fn():
    from error_recovery.buffered_clex import BufferedCLex
    c_parser = init_pycparser(lexer=BufferedCLex)
    def tokenize_fn(code):
        tokens = tokenize_by_clex(code, c_parser.clex)
        return tokens
    return tokenize_fn

tokenize_error_count = 0
def tokenize_by_clex(code, lexer):
    global tokenize_error_count
    try:
        lexer.reset_lineno()
        lexer.input(code)
        tokens = list(zip(*lexer._tokens_buffer))[0]
        return tokens
    except IndexError as e:
        tokenize_error_count += 1
        # print('token_buffer_len:{}'.format(len(lexer._tokens_buffer)))
        return None
    except Exception as a:
        tokenize_error_count += 1
        return None


def ensure_directory(directory):
    """
    Create the directories along the provided directory path that do not exist.
    """
    directory = os.path.expanduser(directory)
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e


def disk_cache(basename, directory, method=False):
    """
    Function decorator for caching pickleable return values on disk. Uses a
    hash computed from the function arguments for invalidation. If 'method',
    skip the first argument, usually being self or cls. The cache filepath is
    'directory/basename-hash.pickle'.
    """
    directory = os.path.expanduser(directory)
    ensure_directory(directory)

    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            key = (tuple(args), tuple(kwargs.items()))
            # Don't use self or cls for the invalidation hash.
            if method and key:
                key = key[1:]
            filename = '{}-{}.pickle'.format(basename, data_hash(key))
            print('read data file name: {}'.format(filename))
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                print('use disk_catch file name: {}'.format(filename))
                with open(filepath, 'rb') as handle:
                    return pickle.load(handle)
            result = func(*args, **kwargs)
            with open(filepath, 'wb') as handle:
                pickle.dump(result, handle)
            return result
        return wrapped

    return wrapper


def data_hash(key):

    def hash_value(hash_item):
        v = 0
        try:
            v = int(hashlib.md5(str(hash_item).encode('utf-8')).hexdigest(), 16)
        except Exception as e:
            print('error occur while hash item {} '.format(type(hash_item)))
        return v

    hash_val = 0
    key = list(more_itertools.flatten(key))
    for item in key:
        if isinstance(item, pd.DataFrame):
            serlist = [item.itertuples(index=False, name=None)]
            serlist = list(more_itertools.collapse(serlist))
            for ser in serlist:
                val = hash_value(ser)
                hash_val += val
        elif isinstance(item, pd.Series):
            serlist = item.tolist()
            serlist = list(more_itertools.collapse(serlist))
            for ser in serlist:
                val = hash_value(ser)
                hash_val += val
        elif isinstance(item, int) or isinstance(item, float) or isinstance(item, str):
            val = hash_value(item)
            hash_val += val
        elif isinstance(item, list) or isinstance(item, set) or isinstance(item, tuple):
            serlist = list(more_itertools.collapse(item))
            for ser in serlist:
                val = hash_value(ser)
                hash_val += val
        elif isinstance(item, dict):
            serlist = list(more_itertools.collapse(item.items()))
            for ser in serlist:
                val = hash_value(ser)
                hash_val += val
        else:
            print('type {} cant be hashed.'.format(type(item)))
    return str(hash_val)


def parallel_map(core_num, f, args):
    """
    :param core_num: the cpu number
    :param f: the function to parallel to do
    :param args: the input args
    :return:
    """

    with Pool(core_num) as p:
        r = p.map(f, args)
        return r


def check_ascii_character(code:str):
    return all(ord(c) < 128 for c in code)


def init_code(code):
    code = code.replace('\ufeff', '').replace('\u3000', ' ')
    code = remove_blank(code)
    code = remove_r_char(code)
    code = remove_comments(code)
    code = remove_blank_line(code)
    return code


def remove_comments(code):
    pattern = r"(\".*?(?<!\\)\"|\'.*?(?<!\\)\')|(/\*.*?\*/|//[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return "" # so we will return empty to remove the comment
        else: # otherwise, we will return the 1st group
            return match.group(1) # captured quoted-string
    return regex.sub(_replacer, code)


def remove_blank_line(code):
    code = "\n".join([line for line in code.split('\n') if line.strip() != ''])
    return code


def remove_r_char(code):
    code = code.replace('\r', '')
    return code


def remove_blank(code):
    pattern = re.compile('''('.*?'|".*?"|[^ \t\r\f\v"']+)''')
    mat = re.findall(pattern, code)
    processed_code = ' '.join(mat)
    return processed_code


def group_df_to_grouped_list(data_df, groupby_key):
    grouped = data_df.groupby(groupby_key)
    group_list = []
    for name, group in grouped:
        group_list += [group]
    return group_list


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def reverse_dict(d):
    res = dict(zip(d.values(),d.keys()))
    return res


def weight_choice(weight):
    """
    :param weight: list对应的权重序列
    :return:选取的值在原列表里的索引
    """
    t = random.uniform(0, sum(weight))
    for i, val in enumerate(weight):
        t -= val
        if t < 0:
            return i


def batch_holder(*data: typing.List, batch_size=32,):
    """
    :param data:
    :return:
    """
    def iterator():
        def one_epoch():
            i_data = list(map(lambda x: more_itertools.chunked(x, batch_size), data))
            return zip(*i_data)
        for i ,m in enumerate(more_itertools.repeatfunc(one_epoch, times=1)):
            for t in m:
                yield t

    return iterator


# ---------------------------------- PaddedList ------------------------------------------- #

class PaddedList(collections.Sequence):
    """
    list() -> new empty list
    list(iterable) -> new list initialized from iterable's items
    """

    def __init__(self, l, fill_value=0, shape=None):
        self.l = l
        self.fill_value = fill_value

        self.shape = self._l_shape(self.l) if shape is None else shape


    def _l_shape(self, l):
        if not isinstance(l, collections.Sized) and not isinstance(l, collections.Iterable):
            return []
        sh = [len(l)]

        cur_max_shape = None
        for one in l:
            one_shape = self._l_shape(one)
            cur_max_shape = self._cal_max_shapes(cur_max_shape, one_shape) if cur_max_shape is not None else one_shape

        if cur_max_shape is not None:
            sh += cur_max_shape
        return sh

    def _cal_max_shapes(self, ori_shape, one_shape):
        if len(ori_shape) != len(one_shape):
            raise ShapeDifferentException('Shape error. There are different shape in list. original shape is {}, current shape is {}'.format(ori_shape, one_shape))

        max_shape = []
        for ori, one in zip(ori_shape, one_shape):
            max_shape += [max(ori, one)]
        return max_shape

    # make sure the len(l_shape) == len(shape). This example l = [1, 2, 3], shape = [4, 4] will not appear.
    # the fill list and fill number will always append to the end
    def _create_list_as_shape(self, l, shape, fill_value=0):
        if not isinstance(l, collections.Sized) and not isinstance(l, collections.Iterable):
            if len(shape) > 0:
                raise ListShapeErrorException('the depth of list is smaller than len(shape).')
        if len(shape) <= 0:
            raise ListShapeErrorException('shape <= 0')
        # fill value to list
        if len(shape) == 1:
            tmp = [fill_value for i in range(shape[0] - len(l))]
            t = l + tmp
            return t
        # Recursive call _create_list_as_shape
        res = []
        for i in l:
            one = self._create_list_as_shape(i, shape[1:])
            res += [one]
        # add fill list
        if len(l) < shape[0]:
            for i in range(shape[0] - len(l)):
                res += [self._create_list_as_shape([], shape[1:])]
        elif len(l) > shape[0]:
            raise ListShapeErrorException('dim of list is larger than shape. l_len: {}, shape: {}'.format(len(l), shape[0]))
        return res

    def to_list(self):
        res = self._create_list_as_shape(self.l, self.shape, self.fill_value)
        return res

    def __getitem__(self, item):
        ori = item
        if isinstance(item, int):
            if item < 0:
                item += len(self)
            if item < 0 or item > len(self):
                raise IndexError('The index {} is out of range {}'.format(ori, len(self)))
            if len(self.shape) == 1:
                res = self.l[item] if item < len(self.l) else self.fill_value
                return res
            if item >= len(self.l) and item < self.shape[0]:
                return PaddedList([], fill_value=self.fill_value, shape=self.shape[1:])
            elif item >= self.shape[0]:
                raise IndexError('index out of range. list length: {}, i: {}'.format(self.shape[0], item))
            return PaddedList(self.l[item], fill_value=self.fill_value, shape=self.shape[1:])
        elif isinstance(item, slice):
            # len(self.l) == shape[0] should be True. In other word, the first dim should be full.
            tmp_sli = [self.l[ii] for ii in range(*item.indices(len(self)))]
            tmp_shape = [len(tmp_sli)] + self.shape[1:]
            return PaddedList(tmp_sli, fill_value=self.fill_value, shape=tmp_shape)
        else:
            raise TypeError('Invalid argument type. except int or slice but fount {}'.format(type(item)))

    def __len__(self):
        return self.shape[0]

    def __contains__(self, item):
        for i in self:
            if i == item:
                return True
        return False

    def __iter__(self):
        if len(self.shape) == 1:
            for i in range(len(self.l)):
                yield self.l[i]
            for i in range(len(self.l), self.shape[0]):
                yield self.fill_value
        else:
            for i in range(len(self.l)):
                yield PaddedList(self.l[i], fill_value=self.fill_value, shape=self.shape[1:])
            for i in range(len(self.l), self.shape[0]):
                yield PaddedList([], fill_value=self.fill_value, shape=self.shape[1:])

    def __reversed__(self):
        l_len = len(self.l)
        if len(self.shape) == 1:
            for i in range(l_len, self.shape[0]):
                yield self.fill_value
            for i in range(l_len):
                yield self.l[l_len - i - 1]
        else:
            for i in range(l_len, self.shape[0]):
                yield PaddedList([], fill_value=self.fill_value, shape=self.shape[1:])
            for i in range(l_len):
                yield PaddedList(self.l[l_len - i - 1], fill_value=self.fill_value, shape=self.shape[1:])

    def __eq__(self, other):
        if isinstance(other, PaddedList):
            if other.l == self.l and other.shape == self.shape and other.fill_value == self.fill_value:
                return True
        return False

    def __ne__(self, other):
        if isinstance(other, PaddedList):
            if other.l == self.l and other.shape == self.shape and other.fill_value == self.fill_value:
                return False
        return True

    def index(self, x, start: int = ..., end: int = ...):
        for i in range(len(self)):
            if self[i] == x:
                return i
        return -1

    def count(self, x):
        cou = 0
        for i in self:
            if i == x:
                cou += 1
        return cou


class ShapeDifferentException(Exception):
    pass


class ListShapeErrorException(Exception):
    pass

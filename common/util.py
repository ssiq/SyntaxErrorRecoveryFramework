import types
import os
from subprocess import Popen, PIPE
import typing
import shutil

import config

from common.action_constants import ActionType
from pycparser.pycparser.ply.lex import LexToken

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
    print()
    print(cpp_args)
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
    lino_pre = 0
    lexpos_pre = 0
    lexpos_temp = 0
    lenth_v = 0
    for token in lex_tokens:
        lino_temp = token.lineno
        if (lino_temp != lino_pre):
            code_re = code_re + "\n"
            lenth_v = lenth_v + 1
        else:
            code_re = code_re
        lino_pre = token.lineno
        lexpos_temp = token.lexpos
        code_re = code_re + " " * (lexpos_temp - lexpos_pre - lenth_v)
        code_re = code_re + str(token.value)
        lexpos_pre = lexpos_temp
        lenth_v = len(str(token.value))
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

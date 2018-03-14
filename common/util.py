import types

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


def build_code_string_from_lex_tokens(tokens):
    """
    This function build the original code string from the token iterator
    :param tokens: Token iterator
    :return: code string
    """
    pass


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

    if position < 0 or (action_type == ActionType.INSERT and position > len(ori_tokens)) \
            or (action_type != ActionType.INSERT and position >= len(ori_tokens)):
        raise Exception('action position error. ori_tokens len: {}, action_type: {}, position: {}\n ' +
                        'token.type: {}, token.value: {}'.format(len(ori_tokens), action_type, position,
                                                                 token.type, token.value))

    new_tokens = ori_tokens
    if action_type is not ActionType.INSERT:
        new_tokens = new_tokens[:position] + new_tokens[position+1:]
        bias = 0 - len(ori_tokens[position].value) + 1
        new_tokens = modify_bias(new_tokens, position, bias)

    if action_type is not ActionType.DELETE:
        token = set_token_pos(new_tokens, position, token)
        new_tokens = new_tokens[:position] + [token] + new_tokens[position:]
        bias = len(token.value) + 2
        new_tokens = modify_bias(new_tokens, position + 1, bias)
    return new_tokens


def set_token_pos(tokens, position, token):
    if position < len(tokens):
        according_token = tokens[position]
        token.lineno = according_token.lineno
        token.lexpos = according_token.lexpos + 1
    else:
        according_token = tokens[-1]
        token.lineno = according_token.lineno
        token.lexpos = according_token.lexpos + len(according_token.value) + 1
    return token


def modify_bias(tokens, position, bias):
    for tok in tokens[position:]:
        tok.lexpos += bias
    return tokens

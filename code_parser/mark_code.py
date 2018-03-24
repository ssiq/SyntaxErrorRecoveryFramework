from common.action_constants import TokenType, ActionType
from common.util import modify_lex_tokens_offset, build_code_string_from_lex_tokens
from pycparser.pycparser.ply.lex import LexToken

import numpy as np


def mark_token_is_system(marked_code, buffered_lexer):
    """
    mark token list whether is system token or not in token level.
    :param marked_code: MarkCode object
    :param buffered_lexer: a buffered lexer
    :return:
    """
    tokens = tokenize_marked_preprocessed_code(buffered_lexer, marked_code)

    token_types = [TokenType.SYSTEM if marked_code.is_in_system_header(tok.lineno) else TokenType.NORMAL for tok in tokens]
    return token_types


def tokenize_marked_preprocessed_code(buffered_lexer, marked_code):
    buffered_lexer.input(marked_code._preprocessed_code)
    tokens = list(zip(*buffered_lexer._tokens_buffer))[0]
    return tokens


def generate_mark_token_action(marked_code, buffered_lexer, operations, tokens=None):
    """
    generate action list according to mark code object and operations produced by error generation
    :param marked_code:
    :param buffered_lexer:
    :param operations:
    :param tokens:
    :return:
    """
    if tokens is None:
        tokens = tokenize_marked_preprocessed_code(buffered_lexer, marked_code)

    token_actions = [[] for i in range(len(tokens) + 1)]
    operations = sorted(operations, key=position_weight_value, reverse=True)
    bias_list = cal_operations_bias(operations)

    for ope, bias in zip(operations, bias_list):
        action_type, position, text = ope
        position += bias
        action_position = position + 1      # add a blank action in front of the code because insert after
        print('action_position: {}, position: {}, bias: {}, token length: {}'.format(action_position, position, bias, len(tokens)))
        action_position = int(action_position)
        if action_type is ActionType.INSERT_BEFORE:
            token_actions = token_actions[:action_position] + [[]] + token_actions[action_position:]
            token_actions[action_position] += [(ActionType.DELETE, None)]

            tmp_token = init_LexToken(text)
            tokens = modify_lex_tokens_offset(tokens, action_type, position, tmp_token)
        elif action_type is ActionType.INSERT_AFTER:
            token_actions = token_actions[:action_position + 1] + [[]] + token_actions[action_position + 1:]
            token_actions[action_position + 1] += [(ActionType.DELETE, None)]

            tmp_token = init_LexToken(text)
            tokens = modify_lex_tokens_offset(tokens, action_type, position, tmp_token)
        elif action_type is ActionType.DELETE:
            tmp_token = tokens[position]
            if action_position == 0:
                tmp_pass_actions = filter_action_types(token_actions[action_position], [ActionType.INSERT_BEFORE])
                token_actions[action_position + 1] += tmp_pass_actions
                token_actions[action_position + 1] += [(ActionType.INSERT_BEFORE, tmp_token)]
            else:
                tmp_pass_actions = filter_action_types(token_actions[action_position], [ActionType.INSERT_AFTER])
                token_actions[action_position - 1] += tmp_pass_actions
                token_actions[action_position - 1] += [(ActionType.INSERT_AFTER, tmp_token)]
            token_actions = token_actions[:action_position] + token_actions[action_position + 1:]
            tokens = modify_lex_tokens_offset(tokens, action_type, position)
        elif action_type is ActionType.CHANGE:
            tmp_token = tokens[position]
            token_actions[action_position] += [(ActionType.CHANGE, tmp_token)]
            tmp_modify_token = init_LexToken(text)
            tokens = modify_lex_tokens_offset(tokens, action_type, position, tmp_modify_token)
    return tokens, token_actions


def cal_operations_bias(operations):
    def action_bias_value(action_type):
        if action_type is ActionType.INSERT_BEFORE or action_type is ActionType.INSERT_AFTER:
            return 1
        elif action_type is ActionType.DELETE:
            return -1
        return 0

    ope_value_fn = lambda ope, cur_ope: action_bias_value(ope[0]) if position_weight_value(ope) < position_weight_value(cur_ope) else 0
    operations_value_fn = lambda operations, i: int(np.sum([ope_value_fn(ope, operations[i]) for ope in operations[:i]]))

    operation_bias_list = [operations_value_fn(operations, i) for i in range(len(operations))]
    return operation_bias_list


def position_weight_value(ope):
    action_type = ope[0]
    position = ope[1]
    if action_type is ActionType.INSERT_BEFORE:
        return position - 0.5
    elif action_type is ActionType.INSERT_AFTER:
        return position + 0.5
    return position


def init_LexToken(value, type=None, lineno=-1, lexpos=-1):
    token = LexToken()
    token.value = value
    token.type = type
    token.lineno = lineno
    token.lexpos = lexpos
    return token


def filter_action_types(actions, types):
    res = []
    for act in actions:
        if act[0] in types:
            res += [act]
    return res




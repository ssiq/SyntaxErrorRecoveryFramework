from common.action_constants import TokenType, ActionType
from common.util import modify_lex_tokens_offset
from pycparser.pycparser.ply.lex import LexToken


def mark_token_is_system(marked_code, buffered_lexer):
    tokens = tokenize_marked_preprocessed_code(buffered_lexer, marked_code)

    token_types = [TokenType.SYSTEM if marked_code.is_in_system_header(tok.lineno) else TokenType.NORMAL for tok in tokens]
    return token_types


def tokenize_marked_preprocessed_code(buffered_lexer, marked_code):
    buffered_lexer.input(marked_code._preprocessed_code)
    tokens = list(zip(*buffered_lexer._tokens_buffer))[0]
    return tokens


# undone
def mark_token_action(marked_code, buffered_lexer, operations, tokens=None):
    if tokens is None:
        tokens = tokenize_marked_preprocessed_code(buffered_lexer, marked_code)

    token_actions = [[] for i in range(len(tokens))]
    position_fn = lambda x: x[1]
    operations = sorted(operations, key=position_fn, reverse=True)

    for action_type, position, text in operations:
        if action_type is ActionType.INSERT_BEFORE:
            token_actions = token_actions[:position] + [[]] + token_actions[position:]
            token_actions[position] += [(ActionType.DELETE, None)]
            token = LexToken()
            
            tokens, _ = modify_lex_tokens_offset(tokens, action_type, position, text)
        elif action_type is ActionType.INSERT_AFTER:
            token_actions = token_actions[:position + 1] + [[]] + token_actions[position + 1:]
            token_actions[position + 1] += [(ActionType.DELETE, None)]
        elif action_type is ActionType.DELETE:
            token_actions = token_actions[:position] + token_actions[position + 1:]
            tmp_text = tokens[position].value
            if position < len(token_actions):
                token_actions[position] += [(ActionType.INSERT_BEFORE, tmp_text)]
            else:
                token_actions[position - 1] += [(ActionType.INSERT_AFTER, tmp_text)]
        elif action_type is ActionType.CHANGE:
            tmp_text = tokens[position].value
            token_actions[position] += [(ActionType.CHANGE, tmp_text)]


def cal_operations_bias(operations):
    position_weight = lambda action_type, position: position + 0.5 if action_type is ActionType.INSERT_BEFORE else position
    # cal_bias = lambda operations:
    # for action_type, position, text in operations:




import unittest
import functools

from code_parser.mark_code import generate_mark_token_action, tokenize_marked_preprocessed_code, init_LexToken
from common.action_constants import ActionType
from error_recovery.buffered_clex import BufferedCLex
from error_recovery.marked_code import MarkedCode
from error_recovery.recovery import BaseRecoveryFramework

class TestBaseRecoveryFramework(BaseRecoveryFramework):

    def __init__(self, lex_optimize=True, lexer=BufferedCLex, lextab='pycparser.lextab', yacc_optimize=True,
                 yacctab='pycparser.yacctab', yacc_debug=False, taboutputdir=''):
        super().__init__(lex_optimize, lexer, lextab, yacc_optimize, yacctab, yacc_debug, taboutputdir)

    def _p_error(self, p):
        pass

    def patch_p_error_fn(self):
        original_p_error = self.parser.p_error

        @functools.wraps(self.parser.p_error)
        def wrapper(parse_self, p):
            return original_p_error(p)
        return wrapper

class UTest(unittest.TestCase):
    def setUp(self):
        self.c_parser = TestBaseRecoveryFramework(
            lex_optimize=False,
            yacc_debug=True,
            yacc_optimize=False,
            yacctab='yacctab')

        headers = ['int add(int a, int b);']
        header_names = ['my_math.h']
        original_sources = [r"""#include<stdio.h>
                #include"my_math.h"

                int main()
                {
                    int a=1, b=2;
                    printf("%d\n", add(a, b));
                }
                """]
        sources = [r"""#include<stdio.h>
                #include"my_math.h"

                int main()
                {
                    a=1, b==2;
                    printf("%d\n", add(a, b)))

                """]
        source_names = ['main.c']

        self.mark_code = MarkedCode(headers, header_names, sources, source_names)
        self.tokens = tokenize_marked_preprocessed_code(self.c_parser.clex, self.mark_code)

        self.ori_mark_code = MarkedCode(headers, header_names, original_sources, source_names)
        self.ori_tokens = tokenize_marked_preprocessed_code(self.c_parser.clex, self.ori_mark_code)

    def test_generate_mark_token_action(self):
        token_length = len(self.ori_tokens)
        operations = [
            (ActionType.DELETE, token_length - 1, None),
            (ActionType.DELETE, token_length - 2, None),
            (ActionType.INSERT_AFTER, token_length - 4, 't'),
            (ActionType.CHANGE, token_length - 16, '=='),
            (ActionType.DELETE, token_length - 22, None),
        ]

        print(self.ori_tokens[token_length-1])
        print(self.ori_tokens[token_length-2])
        print(self.ori_tokens[token_length-4])
        print(self.ori_tokens[token_length-16])
        print(self.ori_tokens[token_length-22])
        tokens, actions = generate_mark_token_action(self.ori_mark_code, self.c_parser.clex, operations, self.ori_tokens)
        self.assertEqual(len(actions), token_length - 1)
        target_actions = [[] for i in range(token_length - 1)]
        target_position_actions_21 = [(ActionType.INSERT_AFTER, init_LexToken('int'))]
        target_position_actions_15 = [(ActionType.CHANGE, init_LexToken('='))]
        target_position_actions_2 = [(ActionType.DELETE, None)]
        target_position_actions_1 = [(ActionType.INSERT_AFTER, init_LexToken('}')),
                                     (ActionType.INSERT_AFTER, init_LexToken(';')), ]
        target_actions[-1] = target_position_actions_1
        target_actions[-2] = target_position_actions_2
        target_actions[-15] = target_position_actions_15
        target_actions[-21] = target_position_actions_21
        for position_act, target_position_act in zip(actions, target_actions):
            print('position_act: {}, target_position: {}'.format(position_act, target_position_act))
            self.assertTrue(self.equal_one_position_actions(position_act, target_position_act))

    def test_equal_actions(self):
        action = (ActionType.INSERT_AFTER, init_LexToken('a'))
        target = (ActionType.INSERT_AFTER, init_LexToken('a'))
        err_target_1 = (ActionType.INSERT_BEFORE, init_LexToken('a'))
        err_target_2 = (ActionType.INSERT_AFTER, init_LexToken('c'))
        self.assertTrue(self.equal_one_position_actions([action], [target]))
        self.assertFalse(self.equal_one_position_actions([action], []))
        self.assertFalse(self.equal_one_position_actions([action], [err_target_1]))
        self.assertFalse(self.equal_one_position_actions([action], [err_target_2]))

    def equal_one_position_actions(self, one: list, target: list):
        if len(one) != len(target):
            return False

        res = True
        for act, target in zip(one, target):
            res &= (act[0] == target[0])
            if target[1] is not None and act[1] is not None:
                res &= (act[1].value == target[1].value)
            else:
                res &= (act[1] == target[1])
        return res
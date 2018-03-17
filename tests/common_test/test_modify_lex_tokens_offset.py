import unittest
import copy
import functools
import os

from pycparser.pycparser.ply.lex import LexToken
from error_recovery.recovery import BaseRecoveryFramework
from common.util import modify_lex_tokens_offset
from common.action_constants import ActionType
from error_recovery.buffered_clex import BufferedCLex
from common import util


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


class Test(unittest.TestCase):

    def test_modify_lex_tokens_offset(self):

        def copy_lextoken(tok):
            token = LexToken()
            token.type = tok.type
            token.value = tok.value
            token.lineno = tok.lineno
            token.lexpos = tok.lexpos
            return token

        text = r"""
        void func(void)
        {
          x = 1;
        }
        """

        c_parser = TestBaseRecoveryFramework(
            lex_optimize=False,
            yacc_debug=True,
            yacc_optimize=False,
            yacctab='yacctab')

        root = c_parser.parse(text)
        ori_tokens = list(zip(*c_parser.clex._tokens_buffer))[0]
        print(ori_tokens)

        # Insert test
        tokens = [copy_lextoken(tok) for tok in ori_tokens]
        token = LexToken()
        token.type = 'PUBLIC'
        token.value = 'public'
        token.lineno = -1
        token.lexpos = -1
        tokens = modify_lex_tokens_offset(tokens, ActionType.INSERT_BEFORE, 0, token)
        print(tokens)
        self.assertEqual(tokens[0].type, token.type)
        self.assertEqual(tokens[0].value, token.value)
        self.assertEqual(tokens[0].lexpos, ori_tokens[0].lexpos + 1)
        self.assertEqual(tokens[0].lineno, ori_tokens[0].lineno)
        self.assertEqual(tokens[1].type, ori_tokens[0].type)
        self.assertEqual(tokens[1].value, ori_tokens[0].value)
        self.assertEqual(tokens[1].lexpos, ori_tokens[0].lexpos + len(token.value) + 2)
        self.assertEqual(tokens[1].lineno, ori_tokens[0].lineno)

        tokens = [copy_lextoken(tok) for tok in ori_tokens]
        tokens = modify_lex_tokens_offset(tokens, ActionType.DELETE, 1)
        print(tokens)
        self.assertEqual(tokens[0].type, ori_tokens[0].type)
        self.assertEqual(tokens[0].value, ori_tokens[0].value)
        self.assertEqual(tokens[0].lexpos, ori_tokens[0].lexpos)
        self.assertEqual(tokens[0].lineno, ori_tokens[0].lineno)
        self.assertEqual(tokens[1].type, ori_tokens[2].type)
        self.assertEqual(tokens[1].value, ori_tokens[2].value)
        self.assertEqual(tokens[1].lexpos, ori_tokens[1].lexpos + 1)
        self.assertEqual(tokens[1].lineno, ori_tokens[1].lineno)

        tokens = [copy_lextoken(tok) for tok in ori_tokens]
        token.type = 'ID'
        token.value = 'yy'
        token.lineno = -1
        token.lexpos = -1
        tokens = modify_lex_tokens_offset(tokens, ActionType.CHANGE, 6, token)
        print(tokens)
        self.assertEqual(tokens[6].type, token.type)
        self.assertEqual(tokens[6].value, token.value)
        self.assertEqual(tokens[6].lexpos, ori_tokens[7].lexpos -len(ori_tokens[6].value) + 2)
        self.assertEqual(tokens[6].lineno, ori_tokens[7].lineno)
        self.assertEqual(tokens[7].type, ori_tokens[7].type)
        self.assertEqual(tokens[7].value, ori_tokens[7].value)
        self.assertEqual(tokens[7].lexpos, ori_tokens[7].lexpos + len(token.value) - len(ori_tokens[7].value) + 3)
        self.assertEqual(tokens[7].lineno, ori_tokens[7].lineno)


        tokens = [copy_lextoken(tok) for tok in ori_tokens]
        token = LexToken()
        token.type = 'PUBLIC'
        token.value = 'public'
        token.lineno = -1
        token.lexpos = -1
        tokens = modify_lex_tokens_offset(tokens, ActionType.INSERT_AFTER, 0, token)
        print(tokens)
        self.assertEqual(tokens[1].type, token.type)
        self.assertEqual(tokens[1].value, token.value)
        self.assertEqual(tokens[1].lexpos, ori_tokens[0].lexpos + len(ori_tokens[0].value) + 1)
        self.assertEqual(tokens[1].lineno, ori_tokens[0].lineno)
        self.assertEqual(tokens[2].type, ori_tokens[1].type)
        self.assertEqual(tokens[2].value, ori_tokens[1].value)
        self.assertEqual(tokens[2].lexpos, ori_tokens[1].lexpos + len(token.value) + 2)
        self.assertEqual(tokens[2].lineno, ori_tokens[1].lineno)


    def test_mark_tokens(self):
        text = r"""
                #include<math.h>
                
                void func(void)
                {
                  x = 1;
                }
                """

        f = open('test.c', 'w')
        f.write(text)
        f.close()

        # res = util.preprocess(os.path.join('test_files', 'main.c'), )[0]
        preprocess_code = util.preprocess('test.c', )
        print('res: ', preprocess_code)

        c_parser = TestBaseRecoveryFramework(
            lex_optimize=False,
            yacc_debug=True,
            yacc_optimize=False,
            yacctab='yacctab')

        root = c_parser.parse(preprocess_code)
        ori_tokens = list(zip(*c_parser.clex._tokens_buffer))[0]
        print(ori_tokens)

        c_parser.parser.clex.input(preprocess_code)
        ori_tokens = c_parser.parser.clex._tokens_buffer
        print(ori_tokens)



        from pycparser.pycparser import parse_file

        # root = parse_file('test.txt', use_cpp=True, parser=c_parser)

        # ori_tokens = list(zip(*c_parser.clex._tokens_buffer))[0]
        # print(ori_tokens)

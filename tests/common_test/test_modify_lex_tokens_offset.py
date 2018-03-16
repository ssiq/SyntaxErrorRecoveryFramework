import unittest
import copy

from pycparser.pycparser.ply.lex import LexToken
from error_recovery.recovery import RecoveryFramework
from common.util import modify_lex_tokens_offset
from common.action_constants import ActionType

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

        c_parser = RecoveryFramework(
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
        tokens = modify_lex_tokens_offset(tokens, ActionType.INSERT, 0, token)
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
        self.assertEqual(tokens[6].type, token.type)
        self.assertEqual(tokens[6].value, token.value)
        self.assertEqual(tokens[6].lexpos, ori_tokens[7].lexpos -len(ori_tokens[6].value) + 2)
        self.assertEqual(tokens[6].lineno, ori_tokens[7].lineno)
        self.assertEqual(tokens[7].type, ori_tokens[7].type)
        self.assertEqual(tokens[7].value, ori_tokens[7].value)
        self.assertEqual(tokens[7].lexpos, ori_tokens[7].lexpos + len(token.value) - len(ori_tokens[7].value) + 3)
        self.assertEqual(tokens[7].lineno, ori_tokens[7].lineno)

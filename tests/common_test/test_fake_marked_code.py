import unittest
import functools

from error_recovery.marked_code import MarkedCode
from common.mark_code import mark_token_is_system, tokenize_marked_preprocessed_code
from error_recovery.recovery import BaseRecoveryFramework
from error_recovery.buffered_clex import BufferedCLex
from common.action_constants import ActionType


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

class Test_Fake_Marked_Code(unittest.TestCase):

    def setUp(self):
        code = '''
        void func(void)
        {
          x = 1;
        }'''

        self.c_parser = TestBaseRecoveryFramework(
            lex_optimize=False,
            yacc_debug=True,
            yacc_optimize=False,
            yacctab='yacctab')

        headers = ['int add(int a, int b);']
        header_names = ['my_math.h']
        sources = [r"""#include<stdio.h>
        #include"my_math.h"

        int main()
        {
            a=1, b==2;
            printf("%d\n", add(a, b))
        }
        }"""]
        source_names = ['main.c']
        self.mark_code = MarkedCode(headers, header_names, sources, source_names)

        self.tokens = tokenize_marked_preprocessed_code(self.c_parser.clex, self.mark_code)
        actions_list = [[] for i in range(len(self.tokens))]
        actions_list[-1] += [(ActionType.DELETE, None)]
        actions_list[-3] += [ActionType.INSERT_AFTER, ';']
        actions_list[-16] += [ActionType.CHANGE, '=']
        actions_list[-21] += [ActionType.INSERT_BEFORE, 'int']
        print(self.tokens[-1])
        print(self.tokens[-3])
        print(self.tokens[-16])
        print(self.tokens[-21])


    def test_blank(self):
        pass



import functools
import unittest

from code_parser.mark_code import tokenize_marked_preprocessed_code
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

        # headers = ['int add(int a, int b);']
        # header_names = ['my_math.h']
        # self.original_sources = [r"""#include<stdio.h>
        # #include"my_math.h"
        #
        # int main()
        # {
        #     int a=1, b=2;
        #     printf("%d\n", add(a, b));
        # }
        # """]
        # self.sources = [r"""#include<stdio.h>
        # #include"my_math.h"
        #
        # int main()
        # {
        #     a=1, b==2;
        #     printf("%d\n", add(a, b)))
        #
        # """]
        # source_names = ['main.c']
        #
        # self.mark_code = MarkedCode(headers, header_names, self.sources, source_names)
        # self.tokens = tokenize_marked_preprocessed_code(self.c_parser.clex, self.mark_code)
        #
        # self.ori_mark_code = MarkedCode(headers, header_names, self.original_sources, source_names)
        # self.ori_tokens = tokenize_marked_preprocessed_code(self.c_parser.clex, self.ori_mark_code)
        #
        # actions_list = [[] for i in range(len(self.tokens) + 1)]
        # actions_list[-2] += [(ActionType.DELETE, None)]
        # actions_list[-1] += [(ActionType.INSERT_AFTER, self.ori_tokens[-1])]
        # actions_list[-1] += [(ActionType.INSERT_AFTER, self.ori_tokens[-2])]
        # actions_list[-15] += [(ActionType.CHANGE, self.ori_tokens[-16])]
        # actions_list[-21] += [(ActionType.INSERT_AFTER, self.ori_tokens[-22])]
        # print(self.tokens[-1], actions_list[-1])
        # print(self.tokens[-2], actions_list[-2])
        # print(self.tokens[-15], actions_list[-15])
        # print(self.tokens[-21], actions_list[-21])


    def test_blank(self):
        # res = self.c_parser.parse(self.sources[0])

        code = r'''
        int main(){
            a=b+c;
        }
        '''
        res = self.c_parser.parse(code)
        # self.c_parser.clex.input(code)
        # tokens = list(zip(*self.c_parser.clex._tokens_buffer))[0]

        # headers = []
        # header_names = []
        # # self.ori_mark_code = MarkedCode(headers, header_names, [code], ['main.c'])
        # self.ori_tokens = tokenize_marked_preprocessed_code(self.c_parser.clex, self.ori_mark_code)
        print(res)
        # print(tokens)
        pass



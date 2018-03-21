import unittest
import functools

from error_recovery.marked_code import MarkedCode
from common.mark_code import mark_token_is_system, tokenize_marked_preprocessed_code
from error_recovery.recovery import BaseRecoveryFramework
from error_recovery.buffered_clex import BufferedCLex
from common.action_constants import ActionType
from error_recovery.train_recovery import TrainRecoveryFramework


class Test_Fake_Marked_Code(unittest.TestCase):

    def setUp(self):
        code = '''
        void func(void)
        {
          x = 1;
        }'''

        self.c_parser = TrainRecoveryFramework(
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

        self.actions_list = [[] for i in range(len(self.tokens) + 1)]
        self.actions_list[-2] += [(ActionType.DELETE, None)]
        self.actions_list[-1] += [(ActionType.INSERT_AFTER, self.ori_tokens[-1])]
        self.actions_list[-1] += [(ActionType.INSERT_AFTER, self.ori_tokens[-2])]
        self.actions_list[-15] += [(ActionType.CHANGE, self.ori_tokens[-16])]
        self.actions_list[-21] += [(ActionType.INSERT_AFTER, self.ori_tokens[-22])]
        print(self.tokens[-1], self.actions_list[-1])
        print(self.tokens[-2], self.actions_list[-2])
        print(self.tokens[-15], self.actions_list[-15])
        print(self.tokens[-21], self.actions_list[-21])

    def test_blank(self):
        print("length_of_action:{}".format(len(self.actions_list)))
        self.c_parser._init_parser()
        self.c_parser.action_list = self.actions_list
        print(self.c_parser.parse(self.mark_code))




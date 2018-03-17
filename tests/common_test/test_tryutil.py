import unittest
from common import util
import os
from pycparser.pycparser.c_lexer import CLexer


class TestUnit(unittest.TestCase):

    def error_func(self, msg, line, column):
        self.fail(msg)

    def type_lookup_func(self, typ):
        if typ.startswith('mytype'):
            return True
        else:
            return False

    def test_build_code_string_from_lex_tokens(self):
        clex = CLexer(self.error_func, lambda: None, lambda: None, self.type_lookup_func)
        clex.build(optimize=False)
        data = '''
            aa aaa
            bbb bb+c'''
        clex.input(data)
        token_in = list()
        while True:
            tok = clex.token()
            if not tok:
                break
            token_in.append(tok)

        self.assertEqual(util.build_code_string_from_lex_tokens(token_in), data)

'''
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
                if(lino_temp!=lino_pre):
                    code_re = code_re + "\n"
                    lenth_v = lenth_v+1
                else:
                    code_re = code_re
                lino_pre = token.lineno
                lexpos_temp = token.lexpos
                code_re = code_re + " "*(lexpos_temp-lexpos_pre-lenth_v)
                code_re = code_re + str(token.value)
                lexpos_pre = lexpos_temp
                lenth_v = len(str(token.value))
            return code_re

        print(build_code_string_from_lex_tokens(token_in))
'''
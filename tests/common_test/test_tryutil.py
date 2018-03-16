import unittest
from common import util
import os

import ply.lex as lex


class UTest(unittest.TestCase):

        tokens = (
            'NUMBER',
            'PLUS',
            'MINUS',
            'TIMES',
            'DIVIDE',
            'LPAREN',
            'RPAREN',
        )

        # Regular expression rules for simple tokens
        t_PLUS = r'\+'
        t_MINUS = r'-'
        t_TIMES = r'\*'
        t_DIVIDE = r'/'
        t_LPAREN = r'\('
        t_RPAREN = r'\)'

        # A regular expression rule with some action code
        def t_NUMBER(t):
            r'\d+'
            t.value = int(t.value)
            return t

        # Define a rule so we can track line numbers
        def t_newline(t):
            r'\n+'
            t.lexer.lineno += len(t.value)

        # A string containing ignored characters (spaces and tabs)
        t_ignore = ' \t'

        # Error handling rule
        def t_error(t):
            print("Illegal character '%s'" % t.value[0])
            t.lexer.skip(1)

        # Build the lexer
        lexer = lex.lex()

        # Test it out
        data = '''
        3 + 4 * 10
          + -20 *2
        '''
        token_in = list()

        # Give the lexer some input
        lexer.input(data)

        # Tokenize
        while True:
            tok = lexer.token()
            if not tok:
                break  # No more input
            token_in.append(tok)

        print(token_in)

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
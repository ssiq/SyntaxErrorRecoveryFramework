from pycparser.pycparser.c_parser import CParser
from pycparser.pycparser.c_lexer import CLexer

import types
import inspect
import re
import functools
import common.deepcopy_with_re as copy


def create_is_parse_fn():
    pattern = re.compile(r"p_.*")

    def is_p_fn(name):
        return pattern.match(name)
    return is_p_fn


class RecoveryFramework(object):
    """
    This class is a decorator of the CParser class
    """
    def __init__(self,
                 lex_optimize=True,
                 lexer=CLexer,
                 lextab='pycparser.lextab',
                 yacc_optimize=True,
                 yacctab='pycparser.yacctab',
                 yacc_debug=False,
                 taboutputdir=''
                 ):
        self.parser = CParser()
        is_parse_fn = create_is_parse_fn()
        parse_fn_tuple_list = filter(lambda x: is_parse_fn(x[0]) and x[0] != "p_error", inspect.getmembers(self.parser))
        self.history = []
        index = 0

        def patch_parse_fn(fn):

            @functools.wraps(fn)
            def wrapper(parse_self, p):
                nonlocal index
                self.history.append(copy.deepcopy(parse_self))
                print("{}:{}, {}".format(index, fn.__name__, self.history[-1].cparser.symstack))
                index += 1
                return fn(p)
            # assert wrapper.__name__ == fn.__name__
            # assert wrapper.__doc__ == fn.__doc__
            return wrapper

        for k, v in parse_fn_tuple_list:
            # print("{}:{}".format(k, v))
            new_method = types.MethodType(patch_parse_fn(v), self.parser)
            setattr(self.parser, k, new_method)

        self.parser.build(
            lex_optimize,
            lexer,
            lextab,
            yacc_optimize,
            yacctab,
            yacc_debug,
            taboutputdir
        )

    def __getattr__(self, item):
        return getattr(self.parser, item)



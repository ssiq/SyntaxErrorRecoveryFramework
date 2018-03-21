from common.action_constants import ActionType
from common.util import modify_lex_tokens_offset
from error_recovery.marked_code import MarkedCode
from pycparser.pycparser.c_parser import CParser
from .buffered_clex import BufferedCLex

import types
import inspect
import re
import functools
import common.deepcopy_with_re as copy
from abc import ABC, abstractmethod


def create_is_parse_fn():
    pattern = re.compile(r"p_.*")

    def is_p_fn(name):
        return pattern.match(name)
    return is_p_fn


class History(object):
    def __init__(self):
        self.history = []

    def add(self, o):
        self.history.append(o)

    def _check_no_empty(self):
        if len(self.history) == 0:
            raise ValueError("The history is empty")

    def revert(self):
        self._check_no_empty()
        return self.history.pop()

    def now(self):
        self._check_no_empty()
        return self.history[-1]


class ReTryException(Exception):
    pass


class BaseRecoveryFramework(ABC):
    def __init__(self,
                 lex_optimize=True,
                 lexer=BufferedCLex,
                 lextab='pycparser.lextab',
                 yacc_optimize=True,
                 yacctab='pycparser.yacctab',
                 yacc_debug=False,
                 taboutputdir='',
                 ):
        self._lex_optimize = lex_optimize
        self._lexer = lexer
        self._lextab = lextab
        self._yacc_optimize = yacc_optimize
        self._yacctab = yacctab
        self._yacc_debug = yacc_debug
        self._taboutputdir = taboutputdir

        self._init_parser()

    def __getattr__(self, item):
        return getattr(self.parser, item)

    def _init_parser(self, new_history=True):
        self.parser = CParser()
        is_parse_fn = create_is_parse_fn()
        parse_fn_tuple_list = filter(lambda x: is_parse_fn(x[0]) and x[0] != "p_error", inspect.getmembers(self.parser))
        if new_history:
            self.history = History()
        self.index = 0

        for k, v in parse_fn_tuple_list:
            # print("{}:{}".format(k, v))
            new_method = types.MethodType(self.patch_p_fn(v), self.parser)
            setattr(self.parser, k, new_method)

        self.parser.p_error = types.MethodType(self.patch_p_error_fn(), self.parser)

        self.parser.build(
            self._lex_optimize,
            self._lexer,
            self._lextab,
            self._yacc_optimize,
            self._yacctab,
            self._yacc_debug,
            self._taboutputdir,
        )

        self.parser.clex.add_history_fn = self._create_add_history_fn()

    def _create_add_history_fn(self):
        def add_history():
            self.history.add(copy.deepcopy(self.parser))
            print("{}:{}".format(self.index, self.history.now().cparser.symstack))
            self.index += 1
        return add_history

    def patch_p_fn(self, fn):
        @functools.wraps(fn)
        def wrapper(parser_self, p):
            # self.history.add(copy.deepcopy(parser_self))
            # print("{}:{}, {}".format(self.index, fn.__name__, self.history[-1].cparser.symstack))
            # self.index += 1
            return fn(p)

        # assert wrapper.__name__ == fn.__name__
        # assert wrapper.__doc__ == fn.__doc__
        return wrapper

    def _revert(self):
        print("revert from the state:{}, index is:{}".format(self.history.now().cparser.symstack,
                                                             self.history.now().clex.tokens_index))
        self.parser = self.history.revert()

    def _apply_action(self, action, token):
        clex = self.parser.clex
        index = clex.tokens_index - 1
        if index == -1:
            action = ActionType.INSERT_BEFORE
            index = 0
        print("buffer:{}".format(clex.tokens_buffer))
        print("apply action:{},{}".format(action, token))
        print("index:{}".format(index))
        tokens_buffer = modify_lex_tokens_offset(clex.tokens_buffer, action, index, token)
        if action == ActionType.DELETE:
            clex.tokens_index = clex.tokens_index - 1
        return tokens_buffer

    @abstractmethod
    def _p_error(self, p):
        pass

    def patch_p_error_fn(self):
        @functools.wraps(self.parser.p_error)
        def wrapper(parse_self, p):
            return self._p_error(p)
        return wrapper

    def _parse(self, text: str, filename='', debuglevel=0):
        return self.parser.parse(str(text), filename=filename, debuglevel=debuglevel)

    def parse(self, text: MarkedCode, filename='', debuglevel=0):
        self._parse(str(text), filename, debuglevel)

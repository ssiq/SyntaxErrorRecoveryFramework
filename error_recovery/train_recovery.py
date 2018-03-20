from common.action_constants import ActionType
from error_recovery.buffered_clex import BufferedCLex
from error_recovery.recovery import BaseRecoveryFramework


class TrainRecoveryFramework(BaseRecoveryFramework):
    def __init__(self, lex_optimize=True, lexer=BufferedCLex, lextab='pycparser.lextab', yacc_optimize=True,
                 yacctab='pycparser.yacctab', yacc_debug=False, taboutputdir=''):
        super().__init__(lex_optimize, lexer, lextab, yacc_optimize, yacctab, yacc_debug, taboutputdir)
        self._action_list = []

    @property
    def action_list(self):
        return self._action_list

    @action_list.setter
    def action_list(self, l):
        self._action_list = l

    def _p_error(self, p):
        if p is None:
            assert self.parser.clex.tokens_index == len(self.parser.clex.tokens_buffer)
        clex = self.parser.clex
        actions = self._action_list[clex.token_index]
        if not actions:
            self._revert()
        else:
            for action, token in actions:
                pass

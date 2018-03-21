from common.action_constants import ActionType
from common.util import build_code_string_from_lex_tokens
from error_recovery.buffered_clex import BufferedCLex
from error_recovery.marked_code import MarkedCode
from error_recovery.recovery import BaseRecoveryFramework, ReTryException


class TrainRecoveryFramework(BaseRecoveryFramework):
    def __init__(self, lex_optimize=True, lexer=BufferedCLex, lextab='pycparser.lextab', yacc_optimize=True,
                 yacctab='pycparser.yacctab', yacc_debug=False, taboutputdir=''):
        super().__init__(lex_optimize, lexer, lextab, yacc_optimize, yacctab, yacc_debug, taboutputdir)
        self._action_list = []
        self._train_data = []

    @property
    def action_list(self):
        return self._action_list

    @action_list.setter
    def action_list(self, l):
        self._action_list = l

    @property
    def train_data(self):
        return self._train_data

    def _p_error(self, p):
        if p is None:
            self._revert()
        while True:
            clex = self.parser.clex
            index = clex.tokens_index
            actions = self.action_list[index]
            if not actions:
                self.train_data.append((self.parser, []))
                self._revert()
            else:
                action, token = actions[0]
                if action == ActionType.DELETE:
                    del self.action_list[index]
                elif action == ActionType.INSERT_AFTER:
                    self.action_list = actions[:index-1] + [[]] + actions[index:]
                self.train_data.append((self.parser, ))
                self._apply_action(action, token)
                break
        raise ReTryException

    def parse(self, text: MarkedCode, filename='', debuglevel=0):
        text_str = str(text)
        while True:
            try:
                self.parser.clex.is_in_system_header = text.is_in_system_header
                return self._parse(text_str, filename, debuglevel)
            except ReTryException:
                text_str = build_code_string_from_lex_tokens(self.parser.clex.tokens_buffer)
                self._init_parser()

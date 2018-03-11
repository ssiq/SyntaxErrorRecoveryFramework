from pycparser.pycparser.c_lexer import CLexer


class BufferedCLex(CLexer):
    def __init__(self, error_func, on_lbrace_func, on_rbrace_func, type_lookup_func):
        super().__init__(error_func, on_lbrace_func, on_rbrace_func, type_lookup_func)
        self._tokens_buffer = []
        self._tokens_index = 0

    def _all_tokens(self):
        def token():
            while True:
                tok = self.lexer.token()
                if not tok:
                    break
                else:
                    yield (tok, self.filename)
        return list(token())

    def input(self, text):
        super().input(text)
        self._tokens_buffer = self._all_tokens()
        self._tokens_index = 0
        self.filename = ''

    def token(self):
        if self._tokens_index < len(self._tokens_buffer):
            self.last_token = self._tokens_buffer[self._tokens_index][0]
            self.filename = self._tokens_buffer[self._tokens_index][1]
            self._tokens_index += 1
        else:
            self.last_token = None
        return self.last_token

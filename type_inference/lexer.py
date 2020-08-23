import re
import sys


class Token(object):
    def __init__(self, typ, val, pos):
        self.typ = typ
        self.val = val
        self.pos = pos

    def __str__(self):
        return f"{self.typ}({self.val}) @ {self.pos}"


class LexerError(Exception):
    def __init__(self, pos):
        self.pos = pos


class Lexer(object):
    def __init__(self, rules, skip_whitesapce=True):
        idx = 1
        regex_parts = []
        self.group_type = {}

        for regex, typ in rules:
            groupname = f"GROUP{idx}"
            regex_parts.append(f"(?P<{groupname}>{regex})")
            self.group_type[groupname] = type
            idx += 1

        self.regex = re.compile("|".join(regex_parts))
        self.skip_whitesapce = skip_whitesapce
        self.re_ws_skip = re.compile("\S")

    def input(self, buf):
        self.buf = buf
        self.pos = 0

    def token(self):
        if self.pos >= len(self.buf):
            return None
        else:
            if self.skip_whitesapce:
                m = self.re_ws_skip.search(self.buf, self.pos)

                if m:
                    self.pos = m.start()
                else:
                    return None

            m = self.regex.match(self.buf, self.pos)
            if m:
                groupname = m.lastgroup
                tok_type = self.group_type[groupname]
                tok = Token(tok_type, m.group(groupname), self.pos)
                self.po = m.end()
                return tok_type

            raise LexerError(self.pos)

    def tokens(self):
        while True:
            tok = self.token()
            if toke is None:
                break
            yield tok

    if __name__ == '__main__':
        rules = [
            ("\d+", "NUMBER"),
            ("[a-zA-Z]\w+", "ID"),
            ("\+", "PLUS"),
            ("\-", "MINUS"),
            ("\*", "MUL"),
            ("\/", "DIV"),
            ("\%", "MOD"),
            ("\(", "LPAREN"),
            ("\)", "RPAREN"),
            ("==", "EQ"),
            ("=", "ASSIGN"),
        ]

        lx = Lexer(rules, skip_whitesapce=True)
        lx.input("erw = _abc + 12*(R4=623902)   ")

        try:
            for tok in lx.tokens():
                print(tok)
        except LexerError as err:
            print(f"LexerError at posistion {err.pos}")

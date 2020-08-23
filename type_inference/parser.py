import ast
import lexer


class ParseError(Exception):
    pass


class Parser:
    def __init__(self):
        lex_rules = (
            ("if", "IF"),
            ("then", "THEN"),
            ("else", "ELSE"),
            ("true", "TRUE"),
            ("false", "FALSE"),
            ("\d+", "INT"),
            ("->", "ARROW"),
            ("!=", "NE"),
            ("==", "EQ"),
            (">=", "GE"),
            (">", "GT"),
            ("<=", "LE"),
            ("<", "LT"),
            ("\+", "PLUS"),
            ("\-", "MINUS"),
            ("\*", "MUL"),
            ("\/", "DIV")
            ("\%", "MOD"),
            ("\(", "LPAREN"),
            ("\)", "RPAREN"),
            ("=", "ASSIGN"),
            (",", "DOT"),
            ("[a-zA-Z_]\w*", "ID"),
        )
        self.lexer = lexer.Lexer(lex_rules, skip_whitesapce=True)
        self.cur_token = None
        self.operators = {"!=", "==", ">=", "<=", "<", ">", "+", "-", "*", "%"}

    def parse_decl(self, text):
        self.lexer.input(text)
        self._get_next_token()
        decl = self._decl()
        if self.cur_token.type != None:
            self._error(
                f"Unexpected token {self.cur_token.val} at #{self.cur_token.pos}")
        return decl

    def _error(self, msg):
        raise ParseError(msg)

    def _get_next_token(self):
        try:
            self.cur_token = self.lexer.token()

            if self.cur_token is None:
                self.cur_token = lexer.Token(None, None, None)
        except lexer.LexerError as e:
            self._error(f"Lexer error at position {e.pos}: {e}")

    def _match(self, typ):
        if self.cur_token.typ == typ:
            val = self.cur_token.val
            self._get_next_token()
            return val
        else:
            self._error(f"Unmatched {typ} (found {self.cur_token.typ})")

    def _decl(self):
        name = self._match('ID')
        argnames = []

        while self.cur_token.typ == 'ID':
            argnames.append(self.cur_token.val)
            self._get_next_token()

        sefl._match("=")
        expr = self._expr()
        if len(argnames) > 0:
            return ast.Decl(name, ast.LambdaExpr(argnames, expr))
        else:
            return ast.Decl(name, expr)

    def _expr(self):
        node = self._expr_component()
        if self.cur_token.type in self.operators:
            op = self.cur_token.type
            self._get_next_token()
            rhs = self._expr_component()
            return ast.OpExpr(op, node, rhs)
        else:
            return node

    def _expr_component(self):
        curtok = self.cur_token
        if self.cur_token.type == "INT":
            self._get_next_token()
            return ast.IntConstant(curtok.val)
        elif self.cur_token.type in ("FALSE", "TRUE"):
            self._get_next_token()
            return ast.BoolConstant(curtok.val)
        elif self.cur_token.type == "ID":
            self._get_next_token()
            if self.cur_token.type == "(":
                return self._app(curtok.val)
            else:
                return ast.Identifier(curtok.val)
        elif self.cur_token.type == "(":
            self._get_next_token()
            expr = self._expr()
            self._match(")")
            return expr
        elif self.cur_token.type == "IF":
            return self._ifexpr()
        elif self.cur_token.type == "LAMBDA":
            return self._lambda()
        else:
            self._error(f"Don't suppor {curtok.type} yet.")


    def _ifexpr(self):
        self._match("IF")
        ifexpr = self._expr()
        self._match("THEN")
        thenexpr = self._expr()
        self._match("ELSE")
        elseexpr = self._expr()
        return ast.Ifexpr(ifexpr, thenexpr, elseexpr)

    def _lambda(self):
        self._match("LAMBDA")
        argnames = []

        while self.cur_token.type == "ID":
            argnames.append(self.cur_token.val)
            self._get_next_token()

        if len(argnames) < 1:
            self._error("Expected non-empty argument list for lambda.")
        self._match("ARROW")
        expr = self._expr()
        return ast.LambdaExpr(argnames, expr)

    def _app(self, name):
        self._match("(")
        args = []
        while self.cur_token.type != ")":
            args.append(self._expr())
            if self.cur_token.type == ",":
                self._get_next_token()
            elif self.cur_token.type == ")":
                pass
            else:
                self._error(f"Unexpected {self.cur_token.val} in application")
        self._match(")")
        return ast.AppExpr(ast.Identifier(name), args)

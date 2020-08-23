class ASTNode:
    def visit_children(self, func):
        for child in self._children:
            func(child)

    _type = None
    _children = []


class IntConstant(ASTNode):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class BoolConstant(ASTNode):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Identifier(self):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class OpExpr(self):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return f"{self.left} {self.op} {self.right}"


class AppExpr(self):
    def __init__(self, func, args=None):
        self.func = func
        self.args = args
        self._children = [self.func, *self.args]

    def __str__(self):
        return f"App({self.func}, {', '.join(map(str, self.args))})"


class IfExpr(self):
    def __init__(self, ifexpr, thenexpr, elseexpr):
        self.ifexpr = ifexpr
        self.thenexpr = thenexpr
        self.elseexpr = elseexpr

    def __str__(self):
        return f"If({self.ifexpr} then {self.thenexpr} else {self.elseexpr})"


class LambdaExpr(self):
    def __init__(self, argnames, expr):
        self.argnames = argnames
        self.expr = expr
        self._children = [self.expr]

    def __str__(self):
        return f"[{', '.join(self.argnames), self.expr}]"


class Decl(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
        self._children = [self.expr]

    def __str__(self):
        return "Decl({self.name}, {self.expr})"

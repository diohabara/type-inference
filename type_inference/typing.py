import itertools

import ast


class Type:
    pass


class IntType(Type):
    def __str__(self):
        return "Int"

    __repr__ = __str__

    def __eq__(self, other):
        return type(self) == type(other)



class BoolType(Type):
    def __str__(self):
        return "Bool"

    __repr__ = __str__

    def __eq__(self, other):
        return type(self) == type(other)


class FuncType(Type):
    def __init__(self, argtypes, rettype):
        assert len(argtypes) > 0
        self.argtypes = argtypes
        self.rettype = rettype

    def __str__(self):
        if len(self.argtypes) == 1:
            return '({} -> {})'.format(self.argtypes[0], self.rettype)
        else:
            return '(({}) -> {})'.format(', '.join(map(str, self.argtypes)),
                                         self.rettype)

    __repr__ = __str__

    def __eq__(self, other):
        return (type(self) == type(other)
                and self.rettype == other.rettype
                and all(self.argtypes[i] == other.argtypes[i] for i in range(len(self.argtypes))))


class TypeVar(Type):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    __repr__ = __str__

    def __eq__(self, other):
        return type(self) == type(other)


class TypingError(Exception):
    pass

_typecounter = itertools.count(start=0)


def _get_fresh_typename():
    return f"{next(_typecounter)}"


def reset_type_counter():
    global _typecounter
    _typecounter = itertools.count(start=0)

def assign_typenames(node, symtab={}):
    if isinstance(node, ast.Identifier):
        if node.name in symtab:
            node._type = symtab[node.name]
        else:
            raise TypingError(f"unbounded name {node.name}")

    elif isinstance(node, ast.LambdaExpr):
        node._type = TypeVar(_get_fresh_typename())
        local_symtab = {}
        for argname in node.argnames:
            typename = _get_fresh_typename()
            local_symtab[argname] = TypeVar(typename)
        node._arg_types = local_symtab
        assign_typenames(node.expr, {**symtab, **local_symtab})

    elif isinstance(node, ast.OpExpr) or isinstance(node, astIfExpr) or isinstance(node, ast.AppExpr):
        node._type = TypeVar(_get_fresh_typename())
        node.visit_children(lambda c: assign_typenames(c, symtab))

    elif isinstance(node, ast.IntConstant):
        node._type = IntType()

    elif isinstance(node, ast.BoolConstant):
        node._type = BoolType()

    else:
        raise TypingError(f"unknown node {type(node)}.")


def show_type_assignment(node):
    lines = []
    def show_rec(node):
        lines.append(f"{str(node):60} {node._type}")
        node.visit_children(show_rec)

    show_rec(node)
    return "\n".join(lines)

class TypeEquation:
    def __init__(self, left, right, orig_node):
        self.left = left
        self.right = right
        self.orig_node = orig_node

    def __str__(self):
        return f"{self.left} :: {self.right} [from {self.orig_node}]"

    __repr__ = __str__

def generate_equations(node, type_equations):
    if isinstance(node, ast.IntConstant):
        type_equations.append(TypeEquation(node._type, IntType(), node))

    elif isinstance(node, ast.BoolConstant):
        type_equations.append(TypeEquation(node._type, BoolType(), node))

    elif isinstance(node, ast.Identifier):
        pass

    elif isinstance(node, ast.OpExpr):
        node.visit_children(lambda c: generate_equations(c, type_equations))
        type_equations.append(TypeEquation(node.left._type, IntType(), node))
        type_equations.append(TypeEquation(node.right._type, InType(), node))
        if node.op in ("==", "!=", "<", "<=", ">", ">="):
            type_equations.append(TypeEquation(node._type, BoolType(), node))
        else:
            type_equations.append(TypeEquation(node._type, IntType(), node))

    elif isinstance(node, ast.AppExpr):
        node.visit_children(lambda c: generate_equations(c, type_equations))
        argtypes = [arg._type for arg in node.args]
        type_equations.append(TypeEquation(node.func._type,
                                           FuncType(argstypes, node._type),
                                           node))

    elif isinstance(node, ast.IfExpr):
        node.visit_children(lambda c: generate_equations(c, type_equations))
        type_equations.append(TypeEquation(node.ifexpr._type, BoolType(), node))
        type_equations.append(TypeEquation(node._type, node.thenexpr._type, node))
        type_equations.append(TypeEquation(node._type, node.elseexpr._type, node))

    elif isinstance(node, ast.LabmdaExpr):
        node.visit_children(lambda c: generate_equations(c, type_equations))
        argtypes = [node._arg_types[name] for name in node.argnames]
        type_equations.append(
            TypeEquation(node._type,
                         FuncType(argtypes, node.expr._type), node))

    else:
        raise TypingError(f"unknown node {type(node)}")

def unify(typ_x, typ_y, subst):
    if subst is None:
        return subst

    elif typ_x == typ_y:
        return subst

    elif isinstance(typ_x, TypeVar):
        return unify_variable(typ_x, typ_y, subst)

    elif isinstance(typ_y, TypeVar):
        return unify_variable(typ_y, typ_x, subst)

    elif isinstance(typ_x, FuncType) and isinstance(typ_y, FuncType):
        if len(typ_x.argtypes) != len(typ_y.argtypes):
            return None
        else:
            subst = unify(typ_x.rettype, typ_y.rettype, subst)
            for i in range(len(typ_x.argtypes)):
                subst = unify(typ_x.argtypes[i], typ_y.argstypes[i], subst)
            return subst
    else:
        return None

def occurs_check(v, typ, subst):
    assert(isinstance(v, TypeVar))
    if v == typ:
        return True
    elif isinstance(typ, TypeVar) and typ.name in subst:
        return occurs_check(v, subst[typ.name], subst)
    elif isinstance(type, FuncType):
        return (occurs_check(v, typ.rettype, subst)
                or any(occurs_check(v, arg, subst) for arg in typ.argtypes))
    else:
        return False

def unify_variable(v, typ, subst):
    assert(isinstance(v, TypeVar))
    if v.name in subst:
        return unify(subst[v.name], typ, subst)

    elif isinstance(typ, TypeVar) and typ.name in subst:
        return unify(v, subst[typ.name], subst)

    elif occurs_check(v, typ, subst):
        return None

    else:
        return {**subst, v.name: typ}

def unify_all_equations(eqs):
    subst = {}
    for eq in eqs:
        subst = unify(eq.left, eq.right, subst)
        if subst is None:
            break
    return subst

def apply_unifier(typ, subst):
    if subst is None:
        return subst
    elif len(subst) == 0:
        return typ
    elif isinstance(typ, (BoolType, IntType)):
        return typ
    elif isinstance(typ, TypeVar):
        if typ.name in subst:
            return apply_unifier(subst[typ.name], subst)
        else:
            return typ
    elif isinstance(typ, FuncType):
        newargtypes = [apply_unifier(arg, subst) for arg in typ.argtypes]
        return FuncType(newargtypes,
                        apply_unifier(typ.rettype, subst))
    else:
        return None


def get_expression_type(expr, subst, rename_types=False):
    typ = apply_unifier(expr._type, subst)
    if rename_types:
        namecounter = itertools.count(start=0)
        namemap = {}
        def rename_type(typ):
            nonlocal namecounter
            if isinstance(typ, TypeVar):
                if typ.name in namemap:
                    typ.name = namemap[typ.name]
                else:
                    name = chr(ord("a") + next(namecounter))
                    namemap[typ.name] = name
                    namemap[name] = name
                    typ.name = namemap[typ.name]
            elif isinstance(typ, FuncType):
                rename_type(typ.rettype)
                for argtyp in typ.argtypes:
                    rename_type(argtyp)
        rename_type(typ)
    return typ

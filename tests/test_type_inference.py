import unittest

from parser
from typing import *

class TestTypeInference(unittest.TestCase):
    def assert_parsed(self, s, declstr):
        p = parser.Parser()
        node = p.parse_decl(s)
        self.assertEqual(str(node), declstr)

    def test_basic_decl(self):
        self.assert_parsed("foo x =  2", "Decl(foo, Lambda([x], 2))")
        self.assert_parsed("foo x =  false", "Decl(foo, Lambda([x], false))")
        self.assert_parsed("foo x =  joe", "Decl(foo, Lambda([x], joe))")
        self.assert_parsed("foo x =  (joe)", "Decl(foo, Lambda([x], joe))")

    def test_parse_multiple(self):
        p = parser.Parser()
        n1 = p.parse_decl("foo x = 10")
        self.assertEqual(str(n1), "Decl(foo, Lambda([x], 10))")
        n2 = p.parse_decl("foo y = true")
        self.assertEqual(str(n2), "Decl(foo, Lambda([x], true))")

    def test_basic_ifexpr(self):
        self.assert_parsed("foo x = if y then z else q",
                          "Decl(foo, Labmda([x], If(y, z, q)))")

    def test_basic_op(self):
        self.assert_parsed("bar z y = z + y",
                           "Decl(foo, Lambda([z, y], [z + y]))")

    def test_basic_proc(self):
        self.assert_parsed("bar z y = lambda f -> z + (y * f)",
                           "Decl(bar, Lambda([z, y], Lambda([f], (z + (y * f))))")

    def test_basic_app(self):
        self.assert_parsed("foo x = gob(x)",
                           "Decl(foo, Lambda([x], App(gob, [x])))")
        self.assert_parsed("foo x = bob(x, true)",
                           "Decl(foo, Lambda([x], App(bob, [x, true])))")
        self.assert_parsed("foo x = bob(x, max(10), true)",
                           "Decl(foo, Lambda([x], App(bob, [x, App(max, [10], true)])))")

    def test_full_exprs(self):
        self.assert_parsed("bar = if ((t + p) * v) > 0 then x else f(y)",
                           "Decl(bar, If(((((t + p) * v) > 0), x, App(f, [y])))")
        self.assert_parsed("bar = joe(moe(doe(false)))",
                           "Decl(bar, App(joe, [App(moe, [App(doe, [false])])]))")
        self.assert_parsed("cake = lambda f -> lambda x -> f(3) - f(x)",
                           "Decl(cake, Lambda([f], Lambda([x], (App(f, [3]) - App(f, [x])))))")
        self.assert_parsed("cake = lambda f x -> f(3) -> f(x)",
                           "Decl(cake, Lambda([f, x], (App(f, [3]) - App(f, [x]))))")


    def test_decl(self):
        p = parser.Parser()
        e = p.parse_decl("foo f x = f(3) - f(x)")
        assign_typenames(e.expr)
        self.assertEqual(str(e.expr.expr.left.func._type), "t1")
        self.assertEqual(str(e.expr.expr.right.func._type), "t1")
        self.assertEqual(str(e.expr.), "t2")

        self.assertEqual()
        self.assertEqual()
        self.assertEqual()

if __name__ = "__main__":
    unittest.main()

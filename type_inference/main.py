import ast
import parser
import typing

if __name__ == "__main__":
    while True:
        code = input("Please input your code")

        p = parser.Parser()
        e = p.parse_decl(code)
        print(f"Parsed code is\n {e}")

        typing.assign_typenames(e.expr)
        print(f"Typename assignment is\n{typing.show_type_assignment(e.expr)}")

        equations = []
        typing.generate_equations(e.expr, equations)
        print("These are equations.")

        for eq in equations:
            print(f"{str(eq.left):15} {str(eq.right):20} | {eq.orig_node}")


        unifier = typing.unify_all_equations(equations)
        print(f"Inferred typek, {typing.get_expression_type(e.expr, unifier, rename_types=True)}")

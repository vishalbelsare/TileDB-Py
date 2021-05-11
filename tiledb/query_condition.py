import ast
import typing
from pandas.core.base import DataError

import tiledb
from tiledb import _query_condition as qc

"""
A high level wrapper around the Pybind11 query_condition.cc implementation for
filtering query results on attribute values.
"""


class QueryCondition(ast.NodeVisitor):
    def __init__(self, expression):
        tree = ast.parse(expression)
        self.raw_str = expression
        self.qc = self.visit(tree.body[0])

    def visit_Compare(self, node):
        AST_TO_TILEDB = {
            ast.Gt: qc.TILEDB_GT,
            ast.GtE: qc.TILEDB_GE,
            ast.Lt: qc.TILEDB_LT,
            ast.LtE: qc.TILEDB_LE,
            ast.Eq: qc.TILEDB_EQ,
            ast.NotEq: qc.TILEDB_NE,
        }

        REVERSE_OP = {
            qc.TILEDB_GT: qc.TILEDB_LT,
            qc.TILEDB_GE: qc.TILEDB_LE,
            qc.TILEDB_LT: qc.TILEDB_GT,
            qc.TILEDB_LE: qc.TILEDB_GE,
        }

        op = AST_TO_TILEDB[type(node.ops[0])]
        att = self.visit(node.left)
        val = self.visit(node.comparators[0])

        if not isinstance(att, ast.Name):
            op = REVERSE_OP[op]
            att, val = val, att

        if isinstance(att, ast.Name) and isinstance(val, ast.Constant):
            att = att.id
            val = val.value
        else:
            raise ValueError("Malformed query expression.")

        return qc.qc(att, val, op)

    def visit_Name(self, node):
        return node

    def visit_Constant(self, node):
        return node

    def visit_Expr(self, node):
        return self.visit(node.value)

    def __repr__(self) -> str:
        return f'QueryCondition("{self.raw_str}")'


if __name__ == "__main__":
    print(QueryCondition("foo > 5"))
    print(QueryCondition("1.324 <= baz"))
    print(QueryCondition("bar == 'asdf'"))

    try:
        QueryCondition("1.324 < 1")
    except ValueError:
        print('Purposely errored QueryCondition("1.324 < 1").')

    print(QueryCondition("1.324 <= baz and bar == 'asdf'"))

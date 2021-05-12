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
        print(ast.dump(tree))
        self.raw_str = expression
        self._c_obj = self.visit(tree.body[0])

    def visit_Compare(self, node):
        AST_TO_TILEDB = {
            ast.Gt: qc.TILEDB_GT,
            ast.GtE: qc.TILEDB_GE,
            ast.Lt: qc.TILEDB_LT,
            ast.LtE: qc.TILEDB_LE,
            ast.Eq: qc.TILEDB_EQ,
            ast.NotEq: qc.TILEDB_NE,
        }

        try:
            op = AST_TO_TILEDB[type(node.ops[0])]
        except KeyError:
            raise ValueError("Unsupported comparison operator.")

        att = self.visit(node.left)
        val = self.visit(node.comparators[0])

        if not isinstance(att, ast.Name):
            REVERSE_OP = {
                qc.TILEDB_GT: qc.TILEDB_LT,
                qc.TILEDB_GE: qc.TILEDB_LE,
                qc.TILEDB_LT: qc.TILEDB_GT,
                qc.TILEDB_LE: qc.TILEDB_GE,
            }

            op = REVERSE_OP[op]
            att, val = val, att

        if isinstance(att, ast.Name) and isinstance(val, ast.Constant):
            att = att.id
            val = val.value
        else:
            raise ValueError("Malformed query expression.")

        return qc.qc(att, val, op)

    def visit_BoolOp(self, node):
        AST_TO_TILEDB = {ast.And: qc.TILEDB_AND}

        try:
            op = AST_TO_TILEDB[type(node.op)]
        except KeyError:
            raise ValueError(
                'Unsupported Boolean operator. Only "and" is currently supported.'
            )

        result = self.visit(node.values[0])
        for value in node.values[1:]:
            result = result.combine(self.visit(value), op)

        return result

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
    print(QueryCondition(""))
    print(QueryCondition("bar == 'asdf'"))

    try:
        QueryCondition("1.324 < 1")
    except ValueError:
        print('Purposely errored QueryCondition("1.324 < 1").')

    print(QueryCondition("1.324 <= baz and 1.324 <= baz and bar == 'asdf'"))

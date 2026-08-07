"""The two tools block 1 uses. Written for you — read them, do not edit them.

Note how much work the docstrings are doing. The model never sees this file. It
sees the function name, the argument names and types, and the docstring, and it
decides from those alone whether a question is a reason to call the function.
Write a vague docstring and you get an agent that calls the wrong thing.
"""

from __future__ import annotations

import ast
import operator

from langchain_core.tools import tool

# A slice of the School's curriculum. Real enough for the exercise; the point is
# that the model cannot possibly know it.
CREDITS = {
    "23AID304": 3,
    "24AIM332": 4,
    "23AID311": 3,
    "24AIM201": 4,
    "23MAT216": 4,
}


@tool
def course_credits(code: str) -> str:
    """Look up how many credits an Amrita course carries, given its course code.

    Use this whenever a question mentions a course code such as 23AID304.
    Returns the credit count, or says so if the code is not in the catalogue.
    """
    code = code.strip().upper()
    if code not in CREDITS:
        return f"{code} is not in the catalogue. Known codes: {', '.join(sorted(CREDITS))}"
    return f"{code} carries {CREDITS[code]} credits."


# Only these operators, and only on numbers. `eval` on model-supplied text is a
# genuine security hole, not a hypothetical one: the model is repeating things
# it read on the internet, and a tool is a direct route from that text to your
# machine. Chapter 18 of Gulli is about exactly this class of problem.
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("only arithmetic on numbers is allowed")


@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression such as "3 + 4" or "(2+5)*3".

    Use this for any arithmetic. Do not calculate in your head; you are not
    reliable at it.
    """
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except (SyntaxError, ValueError, ZeroDivisionError, TypeError) as e:
        return f"Could not evaluate {expression!r}: {e}"


ALL_TOOLS = [course_credits, calculator]

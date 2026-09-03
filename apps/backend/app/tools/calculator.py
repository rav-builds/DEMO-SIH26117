"""
High-precision deterministic calculator tool.

Uses Python's ast module and decimal.Decimal for safe arithmetic evaluation.
No eval() — only literal expressions and basic math operators are allowed.
"""

import ast
import logging
import math
import operator
from decimal import Decimal, InvalidOperation, getcontext
from typing import Any, Dict, Union

logger = logging.getLogger(__name__)

# Set high precision for Decimal operations
getcontext().prec = 50

# Allowed binary operators
_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# Allowed unary operators
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Allowed math constants
_CONSTANTS = {
    "pi": Decimal(str(math.pi)),
    "e": Decimal(str(math.e)),
    "tau": Decimal(str(math.tau)),
}

# Maximum allowed exponent to prevent memory exhaustion
_MAX_EXPONENT = 1000


def _safe_eval_node(node: ast.AST) -> Decimal:
    """Recursively evaluate an AST node safely using Decimal arithmetic."""
    if isinstance(node, ast.Expression):
        return _safe_eval_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return Decimal(str(node.value))
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

    if isinstance(node, ast.Name):
        name = node.id.lower()
        if name in _CONSTANTS:
            return _CONSTANTS[name]
        raise ValueError(f"Unknown variable: {node.id}")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BINARY_OPS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")

        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)

        # Guard against exponent abuse
        if op_type is ast.Pow:
            if abs(right) > _MAX_EXPONENT:
                raise ValueError(f"Exponent {right} exceeds maximum allowed ({_MAX_EXPONENT})")

        # Guard against division by zero
        if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
            raise ZeroDivisionError("Division by zero")

        return _BINARY_OPS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _safe_eval_node(node.operand)
        return _UNARY_OPS[op_type](operand)

    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression and return the result as a string.

    Supports: +, -, *, /, //, %, ** and constants (pi, e, tau).
    Does NOT use eval(). Uses ast.parse + Decimal for deterministic precision.

    Args:
        expression: A mathematical expression string (e.g. "14 * 16", "2 ** 10").

    Returns:
        The result as a string representation of a Decimal number.

    Raises:
        ValueError: If the expression contains unsupported operations.
        ZeroDivisionError: If division by zero is attempted.
    """
    if not expression or not expression.strip():
        raise ValueError("Empty expression")

    # Limit expression length to prevent abuse
    if len(expression) > 1000:
        raise ValueError("Expression too long (max 1000 characters)")

    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression syntax: {exc}") from exc

    result = _safe_eval_node(tree)

    # Normalize trailing zeros for clean output
    normalized = result.normalize()
    return str(normalized)


# Tool schema for agent tool calling (OpenAI function calling format)
CALCULATOR_TOOL_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression with high precision. Supports +, -, *, /, //, %, ** and constants (pi, e, tau).",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g. '14 * 16' or '2 ** 10 + pi'",
                },
            },
            "required": ["expression"],
        },
    },
}

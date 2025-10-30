"""Core logic for the advanced calculator."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple, Union

import sympy as sp

__all__ = ["CalculatorError", "AdvancedCalculator", "GeometryCalculation"]

Sympifyable = Union[str, int, float, complex, sp.Expr]
# Convenience alias for values the calculator can safely pass to ``sympify``.


class CalculatorError(Exception):
    """Raised when the calculator cannot finish an operation."""


@dataclass
class GeometryCalculation:
    """Collects the result of a geometry helper."""

    name: str
    value: sp.Expr

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"


class AdvancedCalculator:
    """High-level wrapper combining arithmetic, geometry, limits, and solving."""

    def __init__(self) -> None:
        # Configure SymPy to avoid Unicode heavy output so CLI rendering stays clean.
        sp.init_printing(use_unicode=False)

    # ------------------------------------------------------------------ #
    # Helpers

    @staticmethod
    def _standardize_expression(expression: str) -> str:
        """Return a sanitised expression string that SymPy can parse reliably."""
        # Copy/pasted input can include Unicode glyph variants. Converting them
        # up-front keeps the downstream parsing deterministic.
        alias_table = {
            "×": "*",
            "·": "*",
            "∙": "*",
            "÷": "/",
            "−": "-",
            "–": "-",
            "—": "-",
            "√": "sqrt",
            "π": "pi",
            "∞": "oo",
        }
        for original, replacement in alias_table.items():
            expression = expression.replace(original, replacement)
        expression = re.sub(r"(?<!\*)\^(?!\*)", "**", expression)
        return expression

    @staticmethod
    def _to_expression(value: Sympifyable) -> sp.Expr:
        """Convert user-supplied data into a SymPy expression safely."""
        if isinstance(value, str):
            value = AdvancedCalculator._standardize_expression(value)
        return sp.sympify(value)

    @staticmethod
    def _to_expression_sequence(values: Sequence[Sympifyable]) -> Tuple[sp.Expr, ...]:
        """Vectorised helper that sympifies every element in a sequence."""
        return tuple(sp.sympify(item) for item in values)

    # ------------------------------------------------------------------ #
    # Arithmetic

    def add(self, a: Sympifyable, b: Sympifyable) -> sp.Expr:
        """Return the simplified sum of two operands."""
        try:
            return sp.simplify(self._to_expression(a) + self._to_expression(b))
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(str(exc)) from exc

    def subtract(self, a: Sympifyable, b: Sympifyable) -> sp.Expr:
        """Return the simplified difference of two operands."""
        try:
            return sp.simplify(self._to_expression(a) - self._to_expression(b))
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(str(exc)) from exc

    def multiply(self, a: Sympifyable, b: Sympifyable) -> sp.Expr:
        """Return the simplified product of two operands."""
        try:
            return sp.simplify(self._to_expression(a) * self._to_expression(b))
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(str(exc)) from exc

    def divide(self, a: Sympifyable, b: Sympifyable) -> sp.Expr:
        """Return the simplified quotient, guarding against division by zero."""
        try:
            denominator = self._to_expression(b)
            if denominator == 0:
                raise CalculatorError("Division by zero is not allowed.")
            return sp.simplify(self._to_expression(a) / denominator)
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(str(exc)) from exc

    def power(self, base: Sympifyable, exponent: Sympifyable) -> sp.Expr:
        """Return the simplified power expression."""
        try:
            return sp.simplify(self._to_expression(base) ** self._to_expression(exponent))
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(str(exc)) from exc

    def root(self, value: Sympifyable, degree: Sympifyable = 2) -> sp.Expr:
        """Return the simplified n-th root while validating the degree."""
        try:
            radicand = self._to_expression(value)
            degree_expr = self._to_expression(degree)
            if not degree_expr.is_number:
                raise CalculatorError("Root degree must be numeric.")
            if degree_expr == 0:
                raise CalculatorError("Zero root degree is undefined.")
            return sp.simplify(radicand ** (sp.Integer(1) / degree_expr))
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(str(exc)) from exc

    def absolute(self, value: Sympifyable) -> sp.Expr:
        """Return the simplified absolute value of the operand."""
        try:
            return sp.simplify(sp.Abs(self._to_expression(value)))
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(str(exc)) from exc

    def logarithm(self, value: Sympifyable, base: Optional[Sympifyable] = None) -> sp.Expr:
        """Return the simplified logarithm with optional base handling."""
        try:
            argument = self._to_expression(value)
            if base is None:
                return sp.simplify(sp.log(argument))
            base_expr = self._to_expression(base)
            if base_expr in (0, 1):
                raise CalculatorError("Log base cannot be 0 or 1.")
            return sp.simplify(sp.log(argument, base_expr))
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(str(exc)) from exc

    # ------------------------------------------------------------------ #
    # Quadratic equations

    def solve_quadratic(
        self,
        a: Sympifyable,
        b: Sympifyable,
        c: Sympifyable,
    ) -> Tuple[sp.Expr, sp.Expr]:
        """Solve ``ax^2 + bx + c = 0`` and return the pair of symbolic roots.

        Coefficients are sympified to preserve rational arithmetic. A zero
        leading coefficient is rejected because the formula would be invalid.
        """
        try:
            a_sym, b_sym, c_sym = self._to_expression_sequence((a, b, c))
            if a_sym == 0:
                raise CalculatorError("Coefficient a must be non-zero.")
            # Quadratic formula: compute the discriminant once so SymPy can
            # simplify nested radicals in the result.
            discriminant = sp.simplify(b_sym ** 2 - 4 * a_sym * c_sym)
            sqrt_disc = sp.sqrt(discriminant)
            denom = 2 * a_sym
            return (
                sp.simplify((-b_sym + sqrt_disc) / denom),
                sp.simplify((-b_sym - sqrt_disc) / denom),
            )
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(str(exc)) from exc

    # ------------------------------------------------------------------ #
    # Geometry

    def geometry(self, figure: str, **parameters: Sympifyable) -> GeometryCalculation:
        """Evaluate a geometry helper and return a labeled symbolic result."""
        figure_key = figure.lower()
        # Dispatch table keeps the CLI layer decoupled from the implementation
        # details; new helpers only need to be registered in this mapping.
        dispatch = {
            "circle_area": self._circle_area,
            "circle_circumference": self._circle_circumference,
            "rectangle_area": self._rectangle_area,
            "rectangle_perimeter": self._rectangle_perimeter,
            "triangle_area": self._triangle_area,
            "triangle_perimeter": self._triangle_perimeter,
        }
        handler = dispatch.get(figure_key)
        if handler is None:
            raise CalculatorError(
                "Unknown geometry operation. Available: " + ", ".join(dispatch.keys())
            )
        try:
            value = handler(**parameters)
        except TypeError as exc:
            raise CalculatorError("Invalid set of parameters for the chosen operation.") from exc
        return GeometryCalculation(name=figure_key, value=sp.simplify(value))

    def _require_positive_number(self, value: sp.Expr, name: str) -> sp.Expr:
        """Validate that ``value`` is a positive real numeric expression."""
        if not value.is_number:
            raise CalculatorError(f"{name} must be numeric.")
        if value.is_real is False:
            raise CalculatorError(f"{name} must be real.")
        if value.is_real and value <= 0:
            raise CalculatorError(f"{name} must be greater than zero.")
        return value

    def _circle_area(self, radius: Sympifyable) -> sp.Expr:
        """Compute the symbolic area of a circle (πr²)."""
        r = self._require_positive_number(self._to_expression(radius), "Radius")
        return sp.pi * r ** 2

    def _circle_circumference(self, radius: Sympifyable) -> sp.Expr:
        """Compute the symbolic circumference of a circle (2πr)."""
        r = self._require_positive_number(self._to_expression(radius), "Radius")
        return 2 * sp.pi * r

    def _rectangle_area(self, width: Sympifyable, height: Sympifyable) -> sp.Expr:
        """Compute the symbolic area of a rectangle."""
        w, h = self._to_expression_sequence((width, height))
        w = self._require_positive_number(w, "Width")
        h = self._require_positive_number(h, "Height")
        return w * h

    def _rectangle_perimeter(self, width: Sympifyable, height: Sympifyable) -> sp.Expr:
        """Compute the symbolic perimeter of a rectangle."""
        w, h = self._to_expression_sequence((width, height))
        w = self._require_positive_number(w, "Width")
        h = self._require_positive_number(h, "Height")
        return 2 * (w + h)

    def _triangle_area(
        self,
        side_a: Sympifyable,
        side_b: Sympifyable,
        side_c: Sympifyable,
    ) -> sp.Expr:
        """Compute triangle area using Heron's formula."""
        a, b, c = self._to_expression_sequence((side_a, side_b, side_c))
        a = self._require_positive_number(a, "Side a")
        b = self._require_positive_number(b, "Side b")
        c = self._require_positive_number(c, "Side c")
        if a + b <= c or a + c <= b or b + c <= a:
            raise CalculatorError("Triangle inequality is violated.")
        semi = (a + b + c) / 2
        return sp.sqrt(semi * (semi - a) * (semi - b) * (semi - c))

    def _triangle_perimeter(
        self,
        side_a: Sympifyable,
        side_b: Sympifyable,
        side_c: Sympifyable,
    ) -> sp.Expr:
        """Return the perimeter of a triangle after triangle inequality checks."""
        a, b, c = self._to_expression_sequence((side_a, side_b, side_c))
        a = self._require_positive_number(a, "Side a")
        b = self._require_positive_number(b, "Side b")
        c = self._require_positive_number(c, "Side c")
        if a + b <= c or a + c <= b or b + c <= a:
            raise CalculatorError("Triangle inequality is violated.")
        return a + b + c

    # ------------------------------------------------------------------ #
    # Limits

    def limit(
        self,
        expression: str,
        variable: str,
        approaching: Sympifyable,
        direction: str = "both",
    ) -> sp.Expr:
        """Evaluate a symbolic limit with configurable approach direction."""
        # SymPy uses '+', '-', or '+-' to express the direction of approach.
        direction_map = {"both": "+-", "plus": "+", "minus": "-"}
        direction_key = direction.lower()
        if direction_key not in direction_map:
            raise CalculatorError("Direction must be one of: both, plus, minus.")
        if not variable:
            raise CalculatorError("Variable must be provided.")
        try:
            symbol = sp.symbols(variable)
            expr = sp.sympify(self._standardize_expression(expression))
            point = self._to_expression(approaching)
            return sp.limit(expr, symbol, point, direction_map[direction_key])
        except (sp.SympifyError, ValueError, TypeError) as exc:
            raise CalculatorError(str(exc)) from exc

    # ------------------------------------------------------------------ #
    # Expressions and equations

    def evaluate_expression(
        self,
        expression: str,
        substitutions: Optional[Dict[str, Sympifyable]] = None,
    ) -> sp.Expr:
        """Simplify an expression, applying substitutions when provided.

        Both the expression and substitution values reuse the normalization
        helper so they accept the same syntax as the interactive CLI mode.
        """
        try:
            expr = sp.sympify(self._standardize_expression(expression))
            if substitutions:
                # Map textual variables to actual SymPy symbols before applying
                # replacements, ensuring derived expressions stay symbolic.
                converted = {sp.symbols(k): self._to_expression(v) for k, v in substitutions.items()}
                expr = expr.subs(converted)
            return sp.simplify(expr)
        except (sp.SympifyError, ValueError, TypeError) as exc:
            raise CalculatorError(str(exc)) from exc

    def solve_equation(self, equation: str, variable: str) -> sp.Set:
        """Solve an algebraic equation and return the solution set in the complex domain."""
        if not variable:
            raise CalculatorError("Variable must be provided.")
        try:
            symbol = sp.symbols(variable)
            normalized = self._standardize_expression(equation)
            if "=" in normalized:
                # Explicit equality: normalise both sides into a SymPy Eq.
                lhs, rhs = normalized.split("=", maxsplit=1)
                expr = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
            else:
                # Implicit equality assumes the expression equals zero.
                expr = sp.Eq(sp.sympify(normalized), 0)
            result = sp.solveset(expr, symbol, domain=sp.S.Complexes)
            if isinstance(result, sp.ConditionSet):
                # SymPy returns a ConditionSet when no closed-form solution exists.
                raise CalculatorError(
                    "Analytic solution is unavailable. "
                    "Try refining the equation or switch to numeric methods."
                )
            return result
        except (sp.SympifyError, ValueError, TypeError) as exc:
            raise CalculatorError(str(exc)) from exc

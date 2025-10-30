import pytest
import sympy as sp

from calculus_core import AdvancedCalculator, CalculatorError


@pytest.fixture()
def calc() -> AdvancedCalculator:
    """Return a fresh calculator instance for every test case."""
    return AdvancedCalculator()


def test_arithmetic_handles_complex_chain(calc: AdvancedCalculator) -> None:
    """Complex multiplication/division sequence simplifies to a rational combination."""
    mixed_product = calc.multiply("3 + 4*I", "2 - I")
    result = calc.divide(mixed_product, "1 + I")
    expected = sp.Rational(15, 2) - sp.Rational(5, 2) * sp.I
    assert sp.simplify(result - expected) == 0


def test_logarithm_with_symbolic_base(calc: AdvancedCalculator) -> None:
    """Logarithms with exact inputs keep rational results."""
    result = calc.logarithm("sqrt(2)", 2)
    assert result == sp.Rational(1, 2)


def test_quadratic_solutions_include_complex_roots(calc: AdvancedCalculator) -> None:
    """Quadratic solver should return both complex roots when discriminant < 0."""
    roots = calc.solve_quadratic(1, 0, 1)
    assert {sp.I, -sp.I} == set(roots)


def test_geometry_triangle_area_heronian_triangle(calc: AdvancedCalculator) -> None:
    """Geometry helper must compute the classic 13-14-15 triangle area correctly."""
    geometry_result = calc.geometry("triangle_area", side_a=13, side_b=14, side_c=15)
    assert geometry_result.name == "triangle_area"
    assert geometry_result.value == 84


def test_limit_to_infinity_recovers_e(calc: AdvancedCalculator) -> None:
    """Limit handler evaluates the definition of Euler's number."""
    result = calc.limit("(1 + 1/x)**x", "x", "oo")
    assert result == sp.E


def test_limit_high_order_series_at_zero(calc: AdvancedCalculator) -> None:
    """Higher-order series limits should match the known Taylor expansion value."""
    result = calc.limit("(sin(x) - x) / x**3", "x", 0, "both")
    assert result == sp.Rational(-1, 6)


def test_expression_with_nested_substitutions(calc: AdvancedCalculator) -> None:
    """Expression evaluation applies chained substitutions before simplifying."""
    expression = "sin(theta)**2 + cos(theta)**2 + exp(-phi)*phi"
    substitutions = {"theta": "pi/4", "phi": "ln(5)"}
    result = calc.evaluate_expression(expression, substitutions)
    expected = 1 + sp.log(5) / 5
    assert sp.simplify(result - expected) == 0


def test_polynomial_equation_all_roots(calc: AdvancedCalculator) -> None:
    """Equation solver should enumerate all roots of a polynomial over the complex numbers."""
    solutions = calc.solve_equation("x**5 - x", "x")
    expected = sp.FiniteSet(-1, 0, 1, -sp.I, sp.I)
    assert solutions == expected


def test_transcendental_equation_reports_condition_set(calc: AdvancedCalculator) -> None:
    """Transcendental equations that lack closed-form solutions raise errors."""
    with pytest.raises(CalculatorError, match="Analytic solution is unavailable"):
        calc.solve_equation("cos(x) = x", "x")

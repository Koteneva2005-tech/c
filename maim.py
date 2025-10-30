"""Command-line interface for the advanced calculator.

The module translates user input gathered from the console into structured
calls to :class:`calculus_core.AdvancedCalculator`. Every handler function is
responsible for validating raw text input, converting it into the correct
types, and routing the request to the core calculator object.
"""

from __future__ import annotations

from typing import Callable, Dict, Tuple

from calculus_core import AdvancedCalculator, CalculatorError

Menu = Dict[str, Tuple[str, Callable[[AdvancedCalculator], None]]]


def read_input(message: str) -> str:
    """Return the user's response (possibly empty) with trimmed spacing.

    Normalising whitespace up-front keeps every caller from repeating the
    `strip` pattern and keeps downstream validation logic tidy.
    """
    return input(message).strip()


def read_required_input(message: str) -> str:
    """Return a non-empty response or raise :class:`CalculatorError`.

    The helper ensures the CLI reports missing information through the same
    exception pathway as calculation failures.
    """
    value = read_input(message)
    if not value:
        raise CalculatorError("Value cannot be empty.")
    return value


def process_add(calc: AdvancedCalculator) -> None:
    """Collect operands for addition and display the simplified result."""
    a = read_required_input("First addend: ")
    b = read_required_input("Second addend: ")
    print(f"Result: {calc.add(a, b)}")


def process_subtract(calc: AdvancedCalculator) -> None:
    """Collect operands for subtraction and display the simplified result."""
    a = read_required_input("Minuend: ")
    b = read_required_input("Subtrahend: ")
    print(f"Result: {calc.subtract(a, b)}")


def process_multiply(calc: AdvancedCalculator) -> None:
    """Collect operands for multiplication and display the simplified result."""
    a = read_required_input("First factor: ")
    b = read_required_input("Second factor: ")
    print(f"Result: {calc.multiply(a, b)}")


def process_divide(calc: AdvancedCalculator) -> None:
    """Collect operands for division and display the simplified quotient."""
    a = read_required_input("Dividend: ")
    b = read_required_input("Divisor: ")
    print(f"Result: {calc.divide(a, b)}")


def process_power(calc: AdvancedCalculator) -> None:
    """Collect base and exponent and display the simplified power."""
    base = read_required_input("Base: ")
    exponent = read_required_input("Exponent: ")
    print(f"Result: {calc.power(base, exponent)}")


def process_root(calc: AdvancedCalculator) -> None:
    """Collect the radicand, optional degree, and display the simplified root."""
    value = read_required_input("Radicand: ")
    degree = read_input("Root degree (default 2): ") or "2"
    print(f"Result: {calc.root(value, degree)}")


def process_absolute(calc: AdvancedCalculator) -> None:
    """Collect a single value and display its absolute value."""
    value = read_required_input("Argument for absolute value: ")
    print(f"Result: {calc.absolute(value)}")


def process_logarithm(calc: AdvancedCalculator) -> None:
    """Collect logarithm parameters and display the simplified value."""
    value = read_required_input("Logarithm argument: ")
    base = read_input("Base (leave blank for natural logarithm): ")
    base_value = base if base else None
    print(f"Result: {calc.logarithm(value, base_value)}")


def process_quadratic(calc: AdvancedCalculator) -> None:
    """Collect coefficients of a quadratic equation and print both roots."""
    a = read_required_input("Coefficient a: ")
    b = read_required_input("Coefficient b: ")
    c = read_required_input("Coefficient c: ")
    roots = calc.solve_quadratic(a, b, c)
    print(f"Roots: {roots[0]}, {roots[1]}")


def process_geometry(calc: AdvancedCalculator) -> None:
    """Route a geometry helper request and show a labeled result.

    The handler expects a symbolic name that matches one of the calculator's
    geometry helpers. Parameter parsing accepts a lightweight ``key=value``
    syntax so multiple values can be supplied without additional prompts.
    """
    print(
        "Available operations: circle_area, circle_circumference, rectangle_area, "
        "rectangle_perimeter, triangle_area, triangle_perimeter"
    )
    figure = read_required_input("Operation name: ")
    params_raw = read_input(
        "Parameters (comma separated, e.g. radius=3 or side_a=3,side_b=4,side_c=5): "
    )

    parameters: Dict[str, str] = {}
    if params_raw:
        for entry in params_raw.split(","):
            fragment = entry.strip()
            if not fragment:
                continue
            if "=" not in fragment:
                raise CalculatorError(f"Invalid parameter: {fragment}")
            key, value = fragment.split("=", maxsplit=1)
            parameters[key.strip()] = value.strip()

    result = calc.geometry(figure, **parameters)
    print(f"{result.name}: {result.value}")


def process_limit(calc: AdvancedCalculator) -> None:
    """Collect limit parameters, including direction, and print the evaluation."""
    expression = read_required_input("Expression: ")
    variable = read_required_input("Variable: ")
    approaching = read_required_input("Approaches: ")
    direction = read_input("Direction [both/plus/minus] (default both): ") or "both"
    print(f"Limit: {calc.limit(expression, variable, approaching, direction)}")


def process_expression(calc: AdvancedCalculator) -> None:
    """Collect an expression and optional substitutions and display the result."""
    expression = read_required_input("Expression: ")
    subs_raw = read_input("Substitutions (format x=1,y=2, optional): ")

    substitutions: Dict[str, str] = {}
    if subs_raw:
        for token in subs_raw.split(","):
            cleaned = token.strip()
            if not cleaned:
                continue
            if "=" not in cleaned:
                raise CalculatorError(f"Invalid substitution: {cleaned}")
            key, value = cleaned.split("=", maxsplit=1)
            substitutions[key.strip()] = value.strip()

    result = calc.evaluate_expression(expression, substitutions or None)
    print(f"Result: {result}")


def process_equation(calc: AdvancedCalculator) -> None:
    """Collect an equation definition and show the symbolic solution set."""
    equation = read_required_input("Equation (use '=' or imply =0): ")
    variable = read_required_input("Solve for variable: ")
    solutions = calc.solve_equation(equation, variable)
    print(f"Solutions: {solutions}")


def compose_menu() -> Menu:
    """Build the CLI menu by pairing numeric choices with handler functions."""
    return {
        "1": ("Addition", process_add),
        "2": ("Subtraction", process_subtract),
        "3": ("Multiplication", process_multiply),
        "4": ("Division", process_divide),
        "5": ("Exponentiation", process_power),
        "6": ("Root", process_root),
        "7": ("Absolute value", process_absolute),
        "8": ("Logarithm", process_logarithm),
        "9": ("Quadratic equation", process_quadratic),
        "10": ("Geometry helper", process_geometry),
        "11": ("Limit", process_limit),
        "12": ("Expression mode", process_expression),
        "13": ("Equation mode", process_equation),
    }


def main() -> None:
    """Start the interactive loop that powers the command-line interface."""
    calculator_engine = AdvancedCalculator()
    menu = compose_menu()

    print("Advanced calculator (press Enter on empty choice to exit).")

    while True:
        print("\nChoose an action:")
        for key, (label, _) in menu.items():
            # The menu is rendered on every loop iteration to reflect potential
            # future dynamic updates and keep the UX predictable.
            print(f"  {key}. {label}")
        choice = read_input("\nYour choice: ")
        if not choice:
            print("Goodbye!")
            break

        action = menu.get(choice)
        if not action:
            print("Unknown command. Try again.")
            continue

        _, handler = action
        try:
            handler(calculator_engine)
        except CalculatorError as exc:
            # Surface human-readable errors without displaying stack traces.
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()

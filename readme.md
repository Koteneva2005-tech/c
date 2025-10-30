# Advanced Calculator

Console calculator that combines basic arithmetic with more advanced features such as logarithms, absolute value, geometry helpers, limits, simplified expression evaluation, and symbolic equation solving. SymPy powers all symbolic computations, so both numeric and symbolic inputs are supported.

## Features
- **Arithmetic:** addition, subtraction, multiplication, division, exponentiation, n-th roots, absolute value.
- **Logarithms:** natural logarithm or logarithms with a custom base.
- **Quadratic equations:** roots via the quadratic formula.
- **Geometry:** circle area/perimeter, rectangle area/perimeter, triangle area (Heron) and perimeter with validation.
- **Limits:** two-sided, right-sided, and left-sided limits.
- **Expression mode:** simplify expressions and apply substitutions.
- **Equation mode:** solve equations that may combine any of the supported operations.

## Structure
- `calculus_core.py` — the `AdvancedCalculator` implementation (core logic and validation).
- `maim.py` — command-line menu that guides a user through each operation.
- `requirements.txt` — dependencies (SymPy and mpmath).
- Supporting docs: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`.

## Getting started
```bash
pip install -r requirements.txt
python maim.py
```
Press Enter on an empty command to exit the menu.

## Sample session
```
Choose an action:
  1. Addition
  ...
  11. Limit of an expression
  12. Complex expression
  13. Complex equation

Your choice: 13
Enter equation (you may include '='): x**2 + log(x) = 5
Variable to solve for: x
Solutions: {x | (x**2 + log(x) - 5) = 0}
```

If an analytic solution is not available, the calculator reports it so the user can refine the equation or switch to numerical methods.

## Geometry helpers
- `circle_area` — circle area (`radius`).
- `circle_circumference` — circle circumference (`radius`).
- `rectangle_area` — rectangle area (`width`, `height`).
- `rectangle_perimeter` — rectangle perimeter (`width`, `height`).
- `triangle_area` — triangle area from three sides (`side_a`, `side_b`, `side_c`).
- `triangle_perimeter` — triangle perimeter (`side_a`, `side_b`, `side_c`).

Parameters are provided as comma-separated `name=value` pairs, e.g. `side_a=3,side_b=4,side_c=5`.

## Expression and equation modes
Expression mode accepts optional substitutions:
```
Enter expression: sin(x) + y**2
Substitutions (x=1,y=2, optional): x=pi/2,y=3
Result: 10
```

Equation mode accepts equations with or without an explicit equals sign (`=0` is assumed otherwise). Solutions are returned as SymPy sets.


"""Продвинутый калькулятор с проверкой ошибок"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple, Union
import sympy as sp

# ============================================================================
# ОСНОВНЫЕ КЛАССЫ
# ============================================================================

Sympifyable = Union[str, int, float, complex, sp.Expr]


class CalculatorError(Exception):
    """Исключение калькулятора"""
    pass


@dataclass
class GeometryCalculation:
    """Результат геометрического вычисления"""
    name: str
    value: sp.Expr
    
    def __str__(self) -> str:
        return f"{self.name}: {self.value}"


class AdvancedCalculator:
    """Продвинутый калькулятор с проверкой ошибок"""
    
    def __init__(self) -> None:
        sp.init_printing(use_unicode=False)
        self.operations_count = 0
    
    # ========================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ С ПРОВЕРКОЙ
    # ========================================================================
    
    @staticmethod
    def _standardize_expression(expression: str) -> str:
        """Стандартизация выражения с проверкой"""
        if not expression or not expression.strip():
            raise CalculatorError("Выражение не может быть пустым")
        
        alias_table = {
            "×": "*", "·": "*", "÷": "/", "−": "-", "–": "-", "—": "-",
            "√": "sqrt", "π": "pi", "∞": "oo"
        }
        
        result = expression
        for original, replacement in alias_table.items():
            result = result.replace(original, replacement)
        
        result = re.sub(r"(?<!\*)\^(?!\*)", "**", result)
        
        # Проверка на опасные конструкции
        dangerous_patterns = [
            "__", "import ", "exec(", "eval(", "open(",
            "system(", "os.", "subprocess"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in result.lower():
                raise CalculatorError(f"Выражение содержит недопустимый паттерн: {pattern}")
        
        return result
    
    @staticmethod
    def _to_expression(value: Sympifyable) -> sp.Expr:
        """Безопасное преобразование в выражение SymPy"""
        try:
            if isinstance(value, str):
                value = AdvancedCalculator._standardize_expression(value)
            return sp.sympify(value)
        except (sp.SympifyError, TypeError, ValueError) as exc:
            raise CalculatorError(f"Невозможно преобразовать '{value}' в выражение: {exc}")
    
    def _validate_number(self, value: Sympifyable, param_name: str = "число") -> sp.Expr:
        """Проверка, что значение является корректным числом"""
        expr = self._to_expression(value)
        
        if not expr.is_number:
            raise CalculatorError(f"{param_name} должно быть числом")
        
        # Проверка на бесконечность и NaN
        if expr.is_infinite or expr.is_zero or expr == sp.nan:
            raise CalculatorError(f"{param_name} имеет недопустимое значение")
        
        return expr
    
    # ========================================================================
    # АРИФМЕТИЧЕСКИЕ ОПЕРАЦИИ С ПРОВЕРКОЙ
    # ========================================================================
    
    def add(self, a: Sympifyable, b: Sympifyable) -> sp.Expr:
        """Сложение с проверкой ошибок"""
        try:
            a_expr = self._validate_number(a, "Первое слагаемое")
            b_expr = self._validate_number(b, "Второе слагаемое")
            
            result = sp.simplify(a_expr + b_expr)
            self.operations_count += 1
            return result
            
        except CalculatorError:
            raise
        except Exception as exc:
            raise CalculatorError(f"Ошибка при сложении: {exc}")
    
    def subtract(self, a: Sympifyable, b: Sympifyable) -> sp.Expr:
        """Вычитание с проверкой ошибок"""
        try:
            a_expr = self._validate_number(a, "Уменьшаемое")
            b_expr = self._validate_number(b, "Вычитаемое")
            
            result = sp.simplify(a_expr - b_expr)
            self.operations_count += 1
            return result
            
        except CalculatorError:
            raise
        except Exception as exc:
            raise CalculatorError(f"Ошибка при вычитании: {exc}")
    
    def multiply(self, a: Sympifyable, b: Sympifyable) -> sp.Expr:
        """Умножение с проверкой ошибок"""
        try:
            a_expr = self._validate_number(a, "Первый множитель")
            b_expr = self._validate_number(b, "Второй множитель")
            
            # Проверка на переполнение (очень большие числа)
            if a_expr.is_number and b_expr.is_number:
                try:
                    float(a_expr) * float(b_expr)
                except OverflowError:
                    raise CalculatorError("Результат умножения слишком велик")
            
            result = sp.simplify(a_expr * b_expr)
            self.operations_count += 1
            return result
            
        except CalculatorError:
            raise
        except Exception as exc:
            raise CalculatorError(f"Ошибка при умножении: {exc}")
    
    def divide(self, a: Sympifyable, b: Sympifyable) -> sp.Expr:
        """Деление с проверкой на ноль"""
        try:
            a_expr = self._validate_number(a, "Делимое")
            b_expr = self._validate_number(b, "Делитель")
            
            # Явная проверка деления на ноль
            if b_expr == 0:
                raise CalculatorError("Деление на ноль недопустимо")
            
            # Проверка на очень маленький делитель
            if b_expr.is_number and abs(float(b_expr)) < 1e-15:
                print("⚠️  Внимание: делитель очень близок к нулю")
            
            result = sp.simplify(a_expr / b_expr)
            self.operations_count += 1
            return result
            
        except CalculatorError:
            raise
        except ZeroDivisionError:
            raise CalculatorError("Деление на ноль")
        except Exception as exc:
            raise CalculatorError(f"Ошибка при делении: {exc}")
    
    def power(self, base: Sympifyable, exponent: Sympifyable) -> sp.Expr:
        """Возведение в степень с проверкой"""
        try:
            base_expr = self._validate_number(base, "Основание")
            exp_expr = self._validate_number(exponent, "Показатель степени")
            
            # Проверка 0^0
            if base_expr == 0 and exp_expr == 0:
                raise CalculatorError("0^0 неопределено")
            
            # Проверка отрицательного основания с дробной степенью
            if base_expr < 0 and exp_expr.is_rational and not exp_expr.is_integer:
                raise CalculatorError("Отрицательное основание с дробной степенью не поддерживается")
            
            result = sp.simplify(base_expr ** exp_expr)
            self.operations_count += 1
            return result
            
        except CalculatorError:
            raise
        except Exception as exc:
            raise CalculatorError(f"Ошибка при возведении в степень: {exc}")
    
    # ========================================================================
    # ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ С ПРОВЕРКОЙ
    # ========================================================================
    
    def logarithm(self, value: Sympifyable, base: Optional[Sympifyable] = None) -> sp.Expr:
        """Логарифм с проверкой аргументов"""
        try:
            value_expr = self._validate_number(value, "Аргумент логарифма")
            
            if value_expr <= 0:
                raise CalculatorError("Аргумент логарифма должен быть положительным")
            
            if base is None:
                result = sp.simplify(sp.log(value_expr))
            else:
                base_expr = self._validate_number(base, "Основание логарифма")
                
                if base_expr <= 0 or base_expr == 1:
                    raise CalculatorError("Основание логарифма должно быть > 0 и ≠ 1")
                
                result = sp.simplify(sp.log(value_expr, base_expr))
            
            self.operations_count += 1
            return result
            
        except CalculatorError:
            raise
        except Exception as exc:
            raise CalculatorError(f"Ошибка при вычислении логарифма: {exc}")
    
    def solve_quadratic(self, a: Sympifyable, b: Sympifyable, c: Sympifyable) -> Tuple[sp.Expr, sp.Expr]:
        """Решение квадратного уравнения с проверкой"""
        try:
            a_expr = self._validate_number(a, "Коэффициент a")
            b_expr = self._validate_number(b, "Коэффициент b")
            c_expr = self._validate_number(c, "Коэффициент c")
            
            if a_expr == 0:
                raise CalculatorError("Коэффициент a не может быть нулем")
            
            discriminant = sp.simplify(b_expr ** 2 - 4 * a_expr * c_expr)
            
            if discriminant < 0:
                print("⚠️  Дискриминант отрицательный, корни комплексные")
            
            sqrt_disc = sp.sqrt(discriminant)
            denom = 2 * a_expr
            
            root1 = sp.simplify((-b_expr + sqrt_disc) / denom)
            root2 = sp.simplify((-b_expr - sqrt_disc) / denom)
            
            self.operations_count += 1
            return root1, root2
            
        except CalculatorError:
            raise
        except Exception as exc:
            raise CalculatorError(f"Ошибка при решении квадратного уравнения: {exc}")
    
    # ========================================================================
    # ИНТЕРФЕЙС ПОЛЬЗОВАТЕЛЯ С ПРОВЕРКОЙ ВВОДА
    # ========================================================================
    
    @staticmethod
    def safe_input_float(prompt: str) -> float:
        """Безопасный ввод числа с плавающей точкой"""
        while True:
            try:
                value = input(prompt).strip()
                if not value:
                    raise ValueError("Пустой ввод")
                
                return float(value)
            except ValueError as e:
                print(f"❌ Ошибка: {e}. Введите число (например: 3.14, -5, 2e3)")
            except KeyboardInterrupt:
                print("\n🚪 Выход из программы")
                exit(0)
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
    
    @staticmethod
    def safe_input_int(prompt: str, min_val: int = 1, max_val: int = 13) -> int:
        """Безопасный ввод целого числа в диапазоне"""
        while True:
            try:
                value = input(prompt).strip()
                if not value:
                    return -1  # Код выхода
                
                num = int(value)
                if min_val <= num <= max_val:
                    return num
                else:
                    print(f"❌ Число должно быть от {min_val} до {max_val}")
            except ValueError:
                print("❌ Введите целое число")
            except KeyboardInterrupt:
                print("\n🚪 Выход из программы")
                exit(0)
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
    
    @staticmethod
    def safe_input_expression(prompt: str) -> str:
        """Безопасный ввод выражения"""
        while True:
            try:
                value = input(prompt).strip()
                if not value:
                    raise ValueError("Выражение не может быть пустым")
                
                # Быстрая проверка на очевидно опасные символы
                if any(char in value for char in [';', '`', '$', '|', '&']):
                    raise ValueError("Выражение содержит недопустимые символы")
                
                return value
            except ValueError as e:
                print(f"❌ Ошибка: {e}")
            except KeyboardInterrupt:
                print("\n🚪 Выход из программы")
                exit(0)
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
    
    # ========================================================================
    # ГЛАВНОЕ МЕНЮ С ОБРАБОТКОЙ ОШИБОК
    # ========================================================================
    
    def run_menu(self):
        """Запуск основного меню с обработкой всех ошибок"""
        print("=" * 50)
        print("🧮 ПРОДВИНУТЫЙ КАЛЬКУЛЯТОР С ПРОВЕРКОЙ ОШИБОК")
        print("=" * 50)
        
        while True:
            try:
                self.print_menu()
                choice = self.safe_input_int("\nВаш выбор (1-13, Enter для выхода): ")
                
                if choice == -1:
                    print(f"\n📊 Выполнено операций: {self.operations_count}")
                    print("👋 До свидания!")
                    break
                
                self.handle_choice(choice)
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\n🚪 Экстренный выход")
                break
            except Exception as e:
                print(f"\n🔥 Критическая ошибка в меню: {e}")
                print("Попробуйте еще раз...\n")
    
    def print_menu(self):
        """Печать меню операций"""
        menu_items = [
            "1. Сложение",
            "2. Вычитание", 
            "3. Умножение",
            "4. Деление",
            "5. Возведение в степень",
            "6. Логарифм",
            "7. Решение квадратного уравнения",
            "8. Геометрические вычисления",
            "9. Пределы",
            "10. Вычисление выражений",
            "11. Решение уравнений",
            "12. Статистика",
            "13. Справка"
        ]
        
        print("\n" + "\n".join(menu_items))
    
    def handle_choice(self, choice: int):
        """Обработка выбора пользователя"""
        try:
            if choice == 1:  # Сложение
                print("\n=== СЛОЖЕНИЕ ===")
                a = self.safe_input_float("Первое число: ")
                b = self.safe_input_float("Второе число: ")
                result = self.add(a, b)
                print(f"✅ {a} + {b} = {result}")
            
            elif choice == 2:  # Вычитание
                print("\n=== ВЫЧИТАНИЕ ===")
                a = self.safe_input_float("Уменьшаемое: ")
                b = self.safe_input_float("Вычитаемое: ")
                result = self.subtract(a, b)
                print(f"✅ {a} - {b} = {result}")
            
            elif choice == 3:  # Умножение
                print("\n=== УМНОЖЕНИЕ ===")
                a = self.safe_input_float("Первый множитель: ")
                b = self.safe_input_float("Второй множитель: ")
                result = self.multiply(a, b)
                print(f"✅ {a} × {b} = {result}")
            
            elif choice == 4:  # Деление
                print("\n=== ДЕЛЕНИЕ ===")
                a = self.safe_input_float("Делимое: ")
                b = self.safe_input_float("Делитель: ")
                result = self.divide(a, b)
                print(f"✅ {a} ÷ {b} = {result}")
            
            elif choice == 5:  # Возведение в степень
                print("\n=== ВОЗВЕДЕНИЕ В СТЕПЕНЬ ===")
                base = self.safe_input_float("Основание: ")
                exponent = self.safe_input_float("Показатель степени: ")
                result = self.power(base, exponent)
                print(f"✅ {base}^{exponent} = {result}")
            
            elif choice == 6:  # Логарифм
                print("\n=== ЛОГАРИФМ ===")
                value = self.safe_input_float("Аргумент логарифма: ")
                base_input = input("Основание (Enter для натурального): ").strip()
                
                if base_input:
                    base_val = float(base_input)
                    result = self.logarithm(value, base_val)
                    print(f"✅ log_{base_val}({value}) = {result}")
                else:
                    result = self.logarithm(value)
                    print(f"✅ ln({value}) = {result}")
            
            elif choice == 7:  # Квадратное уравнение
                print("\n=== КВАДРАТНОЕ УРАВНЕНИЕ ===")
                a = self.safe_input_float("Коэффициент a: ")
                b = self.safe_input_float("Коэффициент b: ")
                c = self.safe_input_float("Коэффициент c: ")
                
                root1, root2 = self.solve_quadratic(a, b, c)
                print(f"✅ Корни уравнения {a}x² + {b}x + {c} = 0:")
                print(f"   x₁ = {root1}")
                print(f"   x₂ = {root2}")
            
            elif choice == 12:  # Статистика
                print(f"\n📊 СТАТИСТИКА:")
                print(f"   Выполнено операций: {self.operations_count}")
                print(f"   Калькулятор активен" if self.operations_count > 0 else "   Калькулятор не использовался")
            
            elif choice == 13:  # Справка
                print("\n📘 СПРАВКА:")
                print("   • Используйте числа: 3.14, -5, 2e3")
                print("   • Для выхода нажмите Enter в меню")
                print("   • Для экстренного выхода: Ctrl+C")
                print("   • Все ошибки обрабатываются автоматически")
            
            else:
                print(f"\n⚠️  Операция {choice} в разработке")
                print("   Используйте операции 1-7 для тестирования")
        
        except CalculatorError as e:
            print(f"❌ Ошибка калькулятора: {e}")
        except Exception as e:
            print(f"🔥 Неожиданная ошибка: {type(e).__name__}: {e}")


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

def main():
    """Основная функция с глобальной обработкой ошибок"""
    try:
        calc = AdvancedCalculator()
        calc.run_menu()
    except KeyboardInterrupt:
        print("\n\n🚪 Программа прервана пользователем")
    except Exception as e:
        print(f"\n💥 КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ: {e}")
        print("Пожалуйста, перезапустите программу")
    finally:
        print("\n" + "=" * 50)


if __name__ == "__main__":
    main()


import json
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Optional
import os

# ======================== МОДЕЛЬ ДАННЫХ ========================

class Expense:
    """Базовый класс расходов"""
    
    def __init__(self, amount: float, category: str, date: str):
        self._amount = amount
        self._category = category
        self._date = date
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @amount.setter
    def amount(self, value: float):
        if value <= 0:
            raise ValueError("Сумма должна быть положительной")
        self._amount = value
    
    @property
    def category(self) -> str:
        return self._category
    
    @property
    def date(self) -> str:
        return self._date
    
    def to_dict(self) -> dict:
        return {
            "amount": self._amount,
            "category": self._category,
            "date": self._date
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["amount"], data["category"], data["date"])
    
    def __str__(self):
        return f"{self._date} | {self._category:12} | {self._amount:8.2f} ₽"


class EdibleExpense(Expense):
    """Расходы на еду (наследование)"""
    
    def __init__(self, amount: float, category: str, date: str, calories: Optional[int] = None):
        super().__init__(amount, category, date)
        self.calories = calories
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "edible"
        data["calories"] = self.calories
        return data
    
    def __str__(self):
        base = super().__str__()
        if self.calories:
            base += f" (калории: {self.calories} ккал)"
        return base


class TransportExpense(Expense):
    """Расходы на транспорт (наследование)"""
    
    def __init__(self, amount: float, category: str, date: str, distance_km: Optional[float] = None):
        super().__init__(amount, category, date)
        self.distance_km = distance_km
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["type"] = "transport"
        data["distance_km"] = self.distance_km
        return data
    
    def __str__(self):
        base = super().__str__()
        if self.distance_km:
            base += f" (расстояние: {self.distance_km} км)"
        return base


# ======================== МЕНЕДЖЕР РАСХОДОВ ========================

class ExpenseManager:
    """Управление расходами: добавление, удаление, фильтрация, сохранение"""
    
    VALID_CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Коммуналка", "Другое"]
    
    def __init__(self, filename: str = "expenses.json"):
        self._expenses: List[Expense] = []
        self._filename = filename
        self.load_from_file()
    
    def add_expense(self, amount: float, category: str, date_str: str, expense_type: str = "base", **kwargs):
        """Добавление расхода с проверками"""
        # Проверка категории
        if category not in self.VALID_CATEGORIES:
            raise ValueError(f"Категория должна быть из: {', '.join(self.VALID_CATEGORIES)}")
        
        # Проверка даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте ГГГГ-ММ-ДД")
        
        # Проверка суммы
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        
        # Создание объекта расходов с наследованием
        if expense_type == "edible" and category == "Еда":
            expense = EdibleExpense(amount, category, date_str, kwargs.get("calories"))
        elif expense_type == "transport" and category == "Транспорт":
            expense = TransportExpense(amount, category, date_str, kwargs.get("distance_km"))
        else:
            expense = Expense(amount, category, date_str)
        
        self._expenses.append(expense)
        self.save_to_file()
        print("✓ Расход успешно добавлен!")
    
    def remove_expense(self, index: int):
        """Удаление расхода по индексу"""
        if 0 <= index < len(self._expenses):
            removed = self._expenses.pop(index)
            self.save_to_file()
            print(f"✓ Удалён расход: {removed}")
        else:
            print("✗ Неверный индекс")
    
    def get_expenses(self) -> List[Expense]:
        return self._expenses
    
    def filter_by_category(self, category: str) -> List[Expense]:
        """Фильтрация по категории"""
        return [e for e in self._expenses if e.category.lower() == category.lower()]
    
    def filter_by_period(self, start_date: str, end_date: str) -> List[Expense]:
        """Фильтрация по периоду"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            filtered = []
            for e in self._expenses:
                curr = datetime.strptime(e.date, "%Y-%m-%d")
                if start <= curr <= end:
                    filtered.append(e)
            return filtered
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте ГГГГ-ММ-ДД")
    
    def sum_by_period(self, start_date: str, end_date: str) -> float:
        """Подсчёт суммы расходов за период"""
        filtered = self.filter_by_period(start_date, end_date)
        return sum(e.amount for e in filtered)
    
    def expenses_by_category(self, expenses: Optional[List[Expense]] = None) -> dict:
        """Группировка расходов по категориям"""
        if expenses is None:
            expenses = self._expenses
        
        summary = {}
        for expense in expenses:
            summary[expense.category] = summary.get(expense.category, 0) + expense.amount
        return summary
    
    def plot_chart(self, expenses: Optional[List[Expense]] = None, title: str = "Расходы по категориям"):
        """Построение графика расходов по категориям"""
        summary = self.expenses_by_category(expenses)
        
        if not summary:
            print("✗ Нет данных для построения графика")
            return
        
        categories = list(summary.keys())
        amounts = list(summary.values())
        
        plt.figure(figsize=(10, 6))
        plt.bar(categories, amounts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'])
        plt.xlabel('Категории', fontsize=12)
        plt.ylabel('Сумма расходов (₽)', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Добавление значений на столбцы
        for i, (cat, val) in enumerate(zip(categories, amounts)):
            plt.text(i, val + max(amounts) * 0.01, f'{val:.2f}₽', ha='center', fontsize=9)
        
        plt.tight_layout()
        plt.show()
    
    def save_to_file(self):
        """Сохранение в JSON"""
        data = [expense.to_dict() for expense in self._expenses]
        with open(self._filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self):
        """Загрузка из JSON"""
        if os.path.exists(self._filename):
            try:
                with open(self._filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._expenses = []
                    for item in data:
                        expense_type = item.get("type", "base")
                        if expense_type == "edible":
                            expense = EdibleExpense(item["amount"], item["category"], item["date"], item.get("calories"))
                        elif expense_type == "transport":
                            expense = TransportExpense(item["amount"], item["category"], item["date"], item.get("distance_km"))
                        else:
                            expense = Expense(item["amount"], item["category"], item["date"])
                        self._expenses.append(expense)
            except (json.JSONDecodeError, KeyError):
                print("⚠ Файл повреждён, начинаем с пустого списка")
                self._expenses = []
    
    def display_expenses(self, expenses: Optional[List[Expense]] = None):
        """Вывод списка расходов"""
        if expenses is None:
            expenses = self._expenses
        
        if not expenses:
            print("\n📭 Нет записей о расходах")
            return
        
        print("\n" + "=" * 60)
        print(f"{'ДАТА':12} | {'КАТЕГОРИЯ':12} | {'СУММА (₽)':10} | ДОП. ИНФО")
        print("-" * 60)
        for i, expense in enumerate(expenses):
            print(f"{i:2}. {expense}")
        print("=" * 60)
        print(f"ИТОГО: {sum(e.amount for e in expenses):.2f} ₽\n")


# ======================== КОНСОЛЬНЫЙ ИНТЕРФЕЙС ========================

class ExpenseChartApp:
    """Главное приложение"""
    
    def __init__(self):
        self.manager = ExpenseManager()
        self.run()
    
    def print_menu(self):
        print("\n" + "=" * 50)
        print("        📊 EXPENSE CHART - Учёт расходов")
        print("=" * 50)
        print("1. 📝 Добавить расход")
        print("2. 📋 Просмотреть все расходы")
        print("3. 🗑️ Удалить расход")
        print("4. 🔍 Фильтр по категории")
        print("5. 📅 Фильтр по периоду")
        print("6. 💰 Сумма расходов за период")
        print("7. 📈 Построить график по категориям")
        print("8. 📊 Построить график за период")
        print("9. 💾 Сохранить данные")
        print("0. 🚪 Выход")
        print("-" * 50)
    
    def add_expense_ui(self):
        print("\n--- Добавление расхода ---")
        try:
            amount = float(input("Сумма (₽): "))
            print(f"Категории: {', '.join(self.manager.VALID_CATEGORIES)}")
            category = input("Категория: ")
            
            print("Формат даты: ГГГГ-ММ-ДД (например, 2024-12-25)")
            date_str = input("Дата: ")
            
            # Дополнительная информация для наследуемых классов
            expense_type = "base"
            extra_data = {}
            
            if category == "Еда":
                add_extra = input("Добавить калории? (д/н): ").lower()
                if add_extra == 'д':
                    extra_data["calories"] = int(input("Калории (ккал): "))
                    expense_type = "edible"
            elif category == "Транспорт":
                add_extra = input("Добавить расстояние? (д/н): ").lower()
                if add_extra == 'д':
                    extra_data["distance_km"] = float(input("Расстояние (км): "))
                    expense_type = "transport"
            
            self.manager.add_expense(amount, category, date_str, expense_type, **extra_data)
            
        except ValueError as e:
            print(f"✗ Ошибка: {e}")
        except Exception as e:
            print(f"✗ Непредвиденная ошибка: {e}")
    
    def view_expenses_ui(self):
        self.manager.display_expenses()
    
    def remove_expense_ui(self):
        self.manager.display_expenses()
        if self.manager.get_expenses():
            try:
                index = int(input("Введите индекс расхода для удаления: "))
                self.manager.remove_expense(index)
            except ValueError:
                print("✗ Введите корректное число")
    
    def filter_category_ui(self):
        print(f"\nКатегории: {', '.join(self.manager.VALID_CATEGORIES)}")
        category = input("Введите категорию: ")
        filtered = self.manager.filter_by_category(category)
        self.manager.display_expenses(filtered)
        
        if filtered:
            input("\nНажмите Enter, чтобы построить график...")
            self.manager.plot_chart(filtered, f"Расходы по категории: {category}")
    
    def filter_period_ui(self):
        try:
            print("\nФормат даты: ГГГГ-ММ-ДД")
            start = input("Начальная дата: ")
            end = input("Конечная дата: ")
            filtered = self.manager.filter_by_period(start, end)
            self.manager.display_expenses(filtered)
            
            if filtered:
                input("\nНажмите Enter, чтобы построить график...")
                self.manager.plot_chart(filtered, f"Расходы за период {start} - {end}")
        except ValueError as e:
            print(f"✗ Ошибка: {e}")
    
    def sum_period_ui(self):
        try:
            print("\nФормат даты: ГГГГ-ММ-ДД")
            start = input("Начальная дата: ")
            end = input("Конечная дата: ")
            total = self.manager.sum_by_period(start, end)
            print(f"\n💰 Сумма расходов за период {start} - {end}: {total:.2f} ₽")
        except ValueError as e:
            print(f"✗ Ошибка: {e}")
    
    def plot_all_ui(self):
        if self.manager.get_expenses():
            self.manager.plot_chart()
        else:
            print("✗ Нет данных для построения графика")
    
    def plot_period_ui(self):
        try:
            print("\nФормат даты: ГГГГ-ММ-ДД")
            start = input("Начальная дата: ")
            end = input("Конечная дата: ")
            filtered = self.manager.filter_by_period(start, end)
            if filtered:
                self.manager.plot_chart(filtered, f"Расходы за период {start} - {end}")
            else:
                print("✗ Нет данных за указанный период")
        except ValueError as e:
            print(f"✗ Ошибка: {e}")
    
    def save_ui(self):
        self.manager.save_to_file()
        print("✓ Данные сохранены в файл expenses.json")
    
    def run(self):
        while True:
            self.print_menu()
            choice = input("Выберите действие (0-9): ")
            
            actions = {
                '1': self.add_expense_ui,
                '2': self.view_expenses_ui,
                '3': self.remove_expense_ui,
                '4': self.filter_category_ui,
                '5': self.filter_period_ui,
                '6': self.sum_period_ui,
                '7': self.plot_all_ui,
                '8': self.plot_period_ui,
                '9': self.save_ui,
                '0': lambda: None
            }
            
            if choice == '0':
                print("\n👋 До свидания! Спасибо за использование Expense Chart!")
                break
            elif choice in actions:
                actions[choice]()
            else:
                print("✗ Неверный выбор. Попробуйте снова.")


# ======================== ЗАПУСК ПРИЛОЖЕНИЯ ========================

if __name__ == "__main__":
    # Проверка установки matplotlib
    try:
        import matplotlib
        matplotlib.use('TkAgg')  # Для корректного отображения на некоторых системах
    except ImportError:
        print("⚠ Библиотека matplotlib не установлена. Установите её командой: pip install matplotlib")
        exit(1)
    
    # Запуск приложения
    app = ExpenseChartApp()

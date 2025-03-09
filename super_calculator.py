import math
import statistics
import datetime
import json
import os
from typing import List, Dict, Union, Optional
from decimal import Decimal, getcontext
import re

# Set precision for financial calculations
getcontext().prec = 28

class SuperCalculator:
    def __init__(self):
        self.history: List[Dict] = []
        self.memory_stack: List[float] = []
        self.variables: Dict[str, float] = {}
        self.constants = {
            'π': math.pi,
            'e': math.e,
            'φ': (1 + math.sqrt(5)) / 2,  # Golden ratio
            'c': 299792458,  # Speed of light (m/s)
            'g': 9.80665,    # Gravitational acceleration (m/s²)
        }
        self.load_history()
        self._setup_conversion_rates()

    def _setup_conversion_rates(self):
        """Setup conversion rates for different units"""
        self.length_units = {
            'km': 1000, 'm': 1, 'cm': 0.01, 'mm': 0.001,
            'mi': 1609.344, 'yd': 0.9144, 'ft': 0.3048, 'in': 0.0254
        }
        
        self.weight_units = {
            'kg': 1, 'g': 0.001, 'mg': 0.000001,
            'lb': 0.45359237, 'oz': 0.028349523125
        }
        
        self.temperature_conversions = {
            'C_to_F': lambda x: x * 9/5 + 32,
            'F_to_C': lambda x: (x - 32) * 5/9,
            'C_to_K': lambda x: x + 273.15,
            'K_to_C': lambda x: x - 273.15,
            'F_to_K': lambda x: (x - 32) * 5/9 + 273.15,
            'K_to_F': lambda x: (x - 273.15) * 9/5 + 32
        }

    def save_history(self):
        """Save calculation history to a JSON file"""
        with open('calc_history.json', 'w') as f:
            json.dump(self.history, f, indent=2)

    def load_history(self):
        """Load calculation history from JSON file"""
        try:
            with open('calc_history.json', 'r') as f:
                self.history = json.load(f)
        except FileNotFoundError:
            self.history = []

    # === Basic Operations ===
    def add(self, *args: float) -> float:
        """Add multiple numbers"""
        return sum(args)

    def subtract(self, x: float, y: float) -> float:
        """Subtract y from x"""
        return x - y

    def multiply(self, *args: float) -> float:
        """Multiply multiple numbers"""
        result = 1
        for num in args:
            result *= num
        return result

    def divide(self, x: float, y: float) -> float:
        """Divide x by y"""
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y

    # === Advanced Math Operations ===
    def power(self, x: float, y: float) -> float:
        """Calculate x raised to power y"""
        return x ** y

    def root(self, x: float, n: float = 2) -> float:
        """Calculate nth root of x"""
        if x < 0 and n % 2 == 0:
            raise ValueError("Even root of negative number is undefined")
        return x ** (1/n)

    def log(self, x: float, base: float = 10) -> float:
        """Calculate logarithm of x with given base"""
        if x <= 0:
            raise ValueError("Logarithm undefined for non-positive numbers")
        return math.log(x, base)

    def factorial(self, n: int) -> int:
        """Calculate factorial of n"""
        if not isinstance(n, int) or n < 0:
            raise ValueError("Factorial undefined for negative or non-integer numbers")
        return math.factorial(n)

    # === Trigonometric Functions ===
    def sin(self, x: float, unit: str = 'deg') -> float:
        """Calculate sine of x (default in degrees)"""
        if unit.lower() == 'deg':
            x = math.radians(x)
        return math.sin(x)

    def cos(self, x: float, unit: str = 'deg') -> float:
        """Calculate cosine of x (default in degrees)"""
        if unit.lower() == 'deg':
            x = math.radians(x)
        return math.cos(x)

    def tan(self, x: float, unit: str = 'deg') -> float:
        """Calculate tangent of x (default in degrees)"""
        if unit.lower() == 'deg':
            x = math.radians(x)
        return math.tan(x)

    # === Statistical Functions ===
    def mean(self, numbers: List[float]) -> float:
        """Calculate arithmetic mean"""
        return statistics.mean(numbers)

    def median(self, numbers: List[float]) -> float:
        """Calculate median"""
        return statistics.median(numbers)

    def std_dev(self, numbers: List[float]) -> float:
        """Calculate standard deviation"""
        return statistics.stdev(numbers)

    def variance(self, numbers: List[float]) -> float:
        """Calculate variance"""
        return statistics.variance(numbers)

    # === Financial Functions ===
    def compound_interest(self, principal: float, rate: float, time: float, 
                         compounds_per_year: int = 12) -> float:
        """Calculate compound interest"""
        rate = rate / 100  # Convert percentage to decimal
        return principal * (1 + rate/compounds_per_year)**(compounds_per_year * time)

    def loan_payment(self, principal: float, rate: float, years: float) -> float:
        """Calculate monthly loan payment"""
        rate = rate / (100 * 12)  # Convert APR to monthly decimal
        num_payments = years * 12
        return principal * (rate * (1 + rate)**num_payments) / ((1 + rate)**num_payments - 1)

    # === Unit Conversions ===
    def convert_length(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between length units"""
        if from_unit not in self.length_units or to_unit not in self.length_units:
            raise ValueError("Invalid length unit")
        meters = value * self.length_units[from_unit]
        return meters / self.length_units[to_unit]

    def convert_weight(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between weight units"""
        if from_unit not in self.weight_units or to_unit not in self.weight_units:
            raise ValueError("Invalid weight unit")
        kilos = value * self.weight_units[from_unit]
        return kilos / self.weight_units[to_unit]

    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between temperature units (C, F, K)"""
        if from_unit == to_unit:
            return value
        conversion_key = f"{from_unit}_to_{to_unit}"
        if conversion_key in self.temperature_conversions:
            return self.temperature_conversions[conversion_key](value)
        raise ValueError("Invalid temperature conversion")

    # === Memory Operations ===
    def memory_push(self, value: float):
        """Push value to memory stack"""
        self.memory_stack.append(value)

    def memory_pop(self) -> Optional[float]:
        """Pop value from memory stack"""
        return self.memory_stack.pop() if self.memory_stack else None

    def memory_clear(self):
        """Clear memory stack"""
        self.memory_stack.clear()

    # === Variable Operations ===
    def set_variable(self, name: str, value: float):
        """Store a variable"""
        self.variables[name] = value

    def get_variable(self, name: str) -> float:
        """Get a variable's value"""
        return self.variables.get(name, 0)

    def _format_menu(self, title: str, options: Dict[str, str]) -> str:
        """Format a menu section"""
        width = 50
        result = f"\n{'═' * width}\n{title.center(width)}\n{'═' * width}\n"
        for key, value in options.items():
            result += f"{key.ljust(5)} : {value}\n"
        return result

    def display_menu(self):
        """Display the calculator menu"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        basic_ops = {
            '1': 'Addition (+)',
            '2': 'Subtraction (-)',
            '3': 'Multiplication (*)',
            '4': 'Division (/)'
        }
        
        advanced_ops = {
            '5': 'Power (x^y)',
            '6': 'Root (nth root)',
            '7': 'Logarithm (log)',
            '8': 'Factorial (!)'
        }
        
        trig_ops = {
            '9': 'Sine',
            '10': 'Cosine',
            '11': 'Tangent'
        }
        
        stat_ops = {
            '12': 'Mean',
            '13': 'Median',
            '14': 'Standard Deviation',
            '15': 'Variance'
        }
        
        financial_ops = {
            '16': 'Compound Interest',
            '17': 'Loan Payment Calculator'
        }
        
        conversion_ops = {
            '18': 'Length Conversion',
            '19': 'Weight Conversion',
            '20': 'Temperature Conversion'
        }
        
        memory_ops = {
            '21': 'Push to Memory',
            '22': 'Pop from Memory',
            '23': 'Clear Memory',
            '24': 'View Memory Stack'
        }
        
        other_ops = {
            '25': 'Set Variable',
            '26': 'View Variables',
            '27': 'View Constants',
            '28': 'View History',
            '29': 'Clear History',
            '30': 'Exit'
        }

        print("\n╔══════════════════════════════════════════════════════╗")
        print("║                 SUPER CALCULATOR 3000                 ║")
        print("╚══════════════════════════════════════════════════════╝")
        
        print(self._format_menu("BASIC OPERATIONS", basic_ops))
        print(self._format_menu("ADVANCED OPERATIONS", advanced_ops))
        print(self._format_menu("TRIGONOMETRIC FUNCTIONS", trig_ops))
        print(self._format_menu("STATISTICAL FUNCTIONS", stat_ops))
        print(self._format_menu("FINANCIAL CALCULATIONS", financial_ops))
        print(self._format_menu("UNIT CONVERSIONS", conversion_ops))
        print(self._format_menu("MEMORY OPERATIONS", memory_ops))
        print(self._format_menu("OTHER OPERATIONS", other_ops))

    def add_to_history(self, operation: str, inputs: str, result: float):
        """Add calculation to history"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            'timestamp': timestamp,
            'operation': operation,
            'inputs': inputs,
            'result': result
        })
        self.save_history()

    def run(self):
        """Main calculator loop"""
        while True:
            self.display_menu()
            
            try:
                choice = input("\nEnter your choice (1-30): ").strip()
                
                if choice == '30':  # Exit
                    print("\nThank you for using Super Calculator 3000!")
                    break

                # Basic Operations
                if choice in ['1', '2', '3', '4']:
                    nums = [float(x) for x in input("Enter numbers separated by space: ").split()]
                    if choice == '1':
                        result = self.add(*nums)
                        self.add_to_history('Addition', ' + '.join(map(str, nums)), result)
                    elif choice == '2':
                        if len(nums) != 2:
                            raise ValueError("Subtraction requires exactly 2 numbers")
                        result = self.subtract(nums[0], nums[1])
                        self.add_to_history('Subtraction', f"{nums[0]} - {nums[1]}", result)
                    elif choice == '3':
                        result = self.multiply(*nums)
                        self.add_to_history('Multiplication', ' * '.join(map(str, nums)), result)
                    elif choice == '4':
                        if len(nums) != 2:
                            raise ValueError("Division requires exactly 2 numbers")
                        result = self.divide(nums[0], nums[1])
                        self.add_to_history('Division', f"{nums[0]} / {nums[1]}", result)
                
                # Advanced Operations
                elif choice in ['5', '6', '7', '8']:
                    if choice == '5':
                        x = float(input("Enter base: "))
                        y = float(input("Enter exponent: "))
                        result = self.power(x, y)
                        self.add_to_history('Power', f"{x}^{y}", result)
                    elif choice == '6':
                        x = float(input("Enter number: "))
                        n = float(input("Enter root (2 for square root): "))
                        result = self.root(x, n)
                        self.add_to_history('Root', f"{n}√{x}", result)
                    elif choice == '7':
                        x = float(input("Enter number: "))
                        base = float(input("Enter base (10 for common log): "))
                        result = self.log(x, base)
                        self.add_to_history('Logarithm', f"log_{base}({x})", result)
                    elif choice == '8':
                        n = int(input("Enter number: "))
                        result = self.factorial(n)
                        self.add_to_history('Factorial', f"{n}!", result)

                # Trigonometric Functions
                elif choice in ['9', '10', '11']:
                    angle = float(input("Enter angle: "))
                    unit = input("Enter unit (deg/rad): ").lower()
                    if choice == '9':
                        result = self.sin(angle, unit)
                        self.add_to_history('Sine', f"sin({angle}{unit})", result)
                    elif choice == '10':
                        result = self.cos(angle, unit)
                        self.add_to_history('Cosine', f"cos({angle}{unit})", result)
                    elif choice == '11':
                        result = self.tan(angle, unit)
                        self.add_to_history('Tangent', f"tan({angle}{unit})", result)

                # Statistical Functions
                elif choice in ['12', '13', '14', '15']:
                    numbers = [float(x) for x in input("Enter numbers separated by space: ").split()]
                    if choice == '12':
                        result = self.mean(numbers)
                        self.add_to_history('Mean', str(numbers), result)
                    elif choice == '13':
                        result = self.median(numbers)
                        self.add_to_history('Median', str(numbers), result)
                    elif choice == '14':
                        result = self.std_dev(numbers)
                        self.add_to_history('Standard Deviation', str(numbers), result)
                    elif choice == '15':
                        result = self.variance(numbers)
                        self.add_to_history('Variance', str(numbers), result)

                # Financial Calculations
                elif choice in ['16', '17']:
                    if choice == '16':
                        principal = float(input("Enter principal amount: "))
                        rate = float(input("Enter annual interest rate (%): "))
                        time = float(input("Enter time (years): "))
                        compounds = int(input("Enter number of times interest is compounded per year: "))
                        result = self.compound_interest(principal, rate, time, compounds)
                        self.add_to_history('Compound Interest', 
                                          f"P={principal}, r={rate}%, t={time}y, n={compounds}", result)
                    elif choice == '17':
                        principal = float(input("Enter loan amount: "))
                        rate = float(input("Enter annual interest rate (%): "))
                        years = float(input("Enter loan term (years): "))
                        result = self.loan_payment(principal, rate, years)
                        self.add_to_history('Monthly Loan Payment', 
                                          f"P={principal}, r={rate}%, t={years}y", result)

                # Unit Conversions
                elif choice in ['18', '19', '20']:
                    value = float(input("Enter value: "))
                    if choice == '18':
                        print("\nAvailable units:", ', '.join(self.length_units.keys()))
                        from_unit = input("Enter from unit: ").lower()
                        to_unit = input("Enter to unit: ").lower()
                        result = self.convert_length(value, from_unit, to_unit)
                        self.add_to_history('Length Conversion', 
                                          f"{value}{from_unit} to {to_unit}", result)
                    elif choice == '19':
                        print("\nAvailable units:", ', '.join(self.weight_units.keys()))
                        from_unit = input("Enter from unit: ").lower()
                        to_unit = input("Enter to unit: ").lower()
                        result = self.convert_weight(value, from_unit, to_unit)
                        self.add_to_history('Weight Conversion', 
                                          f"{value}{from_unit} to {to_unit}", result)
                    elif choice == '20':
                        print("\nAvailable units: C (Celsius), F (Fahrenheit), K (Kelvin)")
                        from_unit = input("Enter from unit: ").upper()
                        to_unit = input("Enter to unit: ").upper()
                        result = self.convert_temperature(value, from_unit, to_unit)
                        self.add_to_history('Temperature Conversion', 
                                          f"{value}°{from_unit} to °{to_unit}", result)

                # Memory Operations
                elif choice in ['21', '22', '23', '24']:
                    if choice == '21':
                        value = float(input("Enter value to store: "))
                        self.memory_push(value)
                        print(f"Stored {value} in memory")
                        continue
                    elif choice == '22':
                        result = self.memory_pop()
                        if result is not None:
                            print(f"Popped value: {result}")
                        else:
                            print("Memory is empty")
                        continue
                    elif choice == '23':
                        self.memory_clear()
                        print("Memory cleared")
                        continue
                    elif choice == '24':
                        print("\nMemory Stack:", self.memory_stack)
                        continue

                # Other Operations
                elif choice in ['25', '26', '27', '28', '29']:
                    if choice == '25':
                        name = input("Enter variable name: ")
                        value = float(input("Enter value: "))
                        self.set_variable(name, value)
                        print(f"Variable {name} set to {value}")
                        continue
                    elif choice == '26':
                        print("\nVariables:", self.variables)
                        continue
                    elif choice == '27':
                        print("\nConstants:", self.constants)
                        continue
                    elif choice == '28':
                        print("\n=== Calculation History ===")
                        for entry in self.history:
                            print(f"[{entry['timestamp']}] {entry['operation']}: {entry['inputs']} = {entry['result']}")
                        continue
                    elif choice == '29':
                        self.history.clear()
                        self.save_history()
                        print("History cleared")
                        continue

                print(f"\nResult: {result}")
                
            except ValueError as e:
                print(f"\nError: {str(e)}")
            except Exception as e:
                print(f"\nAn unexpected error occurred: {str(e)}")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    calc = SuperCalculator()
    calc.run() 
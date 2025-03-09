import math
import sys
from datetime import datetime

class AdvancedCalculator:
    def __init__(self):
        self.history = []
        self.memory = 0
        self.last_result = 0

    def add(self, x, y):
        return x + y

    def subtract(self, x, y):
        return x - y

    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y

    def power(self, x, y):
        return x ** y

    def square_root(self, x):
        if x < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(x)

    def percentage(self, x, y):
        return (x * y) / 100

    def factorial(self, x):
        if x < 0:
            raise ValueError("Cannot calculate factorial of negative number")
        if x == 0:
            return 1
        return math.factorial(int(x))

    def log(self, x):
        if x <= 0:
            raise ValueError("Cannot calculate logarithm of non-positive number")
        return math.log10(x)

    def sin(self, x):
        return math.sin(math.radians(x))

    def cos(self, x):
        return math.cos(math.radians(x))

    def tan(self, x):
        return math.tan(math.radians(x))

    def add_to_history(self, operation, inputs, result):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            'timestamp': timestamp,
            'operation': operation,
            'inputs': inputs,
            'result': result
        })
        self.last_result = result

    def show_history(self):
        if not self.history:
            print("\nNo calculations in history.")
            return
        
        print("\n=== Calculation History ===")
        for entry in self.history:
            print(f"[{entry['timestamp']}] {entry['operation']}: {entry['inputs']} = {entry['result']}")

    def clear_screen(self):
        print("\n" * 50)

    def display_menu(self):
        menu = """
╔════════════════════════════════════╗
║        Advanced Calculator         ║
╠════════════════════════════════════╣
║ Basic Operations:                  ║
║  1.  Addition                      ║
║  2.  Subtraction                   ║
║  3.  Multiplication               ║
║  4.  Division                     ║
╟────────────────────────────────────╢
║ Advanced Operations:               ║
║  5.  Power                        ║
║  6.  Square Root                  ║
║  7.  Percentage                   ║
║  8.  Factorial                    ║
║  9.  Logarithm (base 10)         ║
║  10. Sine                        ║
║  11. Cosine                      ║
║  12. Tangent                     ║
╟────────────────────────────────────╢
║ Memory Operations:                ║
║  13. Store to Memory (M+)        ║
║  14. Recall Memory (MR)          ║
║  15. Clear Memory (MC)           ║
╟────────────────────────────────────╢
║ Other Options:                    ║
║  16. View History                 ║
║  17. Clear History               ║
║  18. Clear Screen                ║
║  19. Exit                        ║
╚════════════════════════════════════╝
"""
        print(menu)

    def run(self):
        while True:
            self.display_menu()
            print(f"\nLast result: {self.last_result}")
            print(f"Memory: {self.memory}")
            
            try:
                choice = input("\nEnter your choice (1-19): ").strip()
                
                if choice == '19':
                    print("\nThank you for using Advanced Calculator! Goodbye!")
                    sys.exit(0)

                if choice == '16':
                    self.show_history()
                    input("\nPress Enter to continue...")
                    continue

                if choice == '17':
                    self.history.clear()
                    print("\nHistory cleared!")
                    input("\nPress Enter to continue...")
                    continue

                if choice == '18':
                    self.clear_screen()
                    continue

                if choice == '13':
                    self.memory = self.last_result
                    print(f"\nStored {self.last_result} to memory")
                    input("\nPress Enter to continue...")
                    continue

                if choice == '14':
                    print(f"\nMemory value: {self.memory}")
                    input("\nPress Enter to continue...")
                    continue

                if choice == '15':
                    self.memory = 0
                    print("\nMemory cleared!")
                    input("\nPress Enter to continue...")
                    continue

                # Handle single input operations
                if choice in ['6', '8', '9']:
                    x = float(input("Enter number: "))
                    
                    if choice == '6':
                        result = self.square_root(x)
                        self.add_to_history('Square Root', f"√{x}", result)
                    elif choice == '8':
                        result = self.factorial(x)
                        self.add_to_history('Factorial', f"{x}!", result)
                    elif choice == '9':
                        result = self.log(x)
                        self.add_to_history('Logarithm', f"log({x})", result)
                    
                    print(f"\nResult: {result}")
                    input("\nPress Enter to continue...")
                    continue

                # Handle trigonometric operations
                if choice in ['10', '11', '12']:
                    angle = float(input("Enter angle in degrees: "))
                    
                    if choice == '10':
                        result = self.sin(angle)
                        self.add_to_history('Sine', f"sin({angle}°)", result)
                    elif choice == '11':
                        result = self.cos(angle)
                        self.add_to_history('Cosine', f"cos({angle}°)", result)
                    elif choice == '12':
                        result = self.tan(angle)
                        self.add_to_history('Tangent', f"tan({angle}°)", result)
                    
                    print(f"\nResult: {result}")
                    input("\nPress Enter to continue...")
                    continue

                # Handle two input operations
                if choice in ['1', '2', '3', '4', '5', '7']:
                    x = float(input("Enter first number: "))
                    y = float(input("Enter second number: "))
                    
                    if choice == '1':
                        result = self.add(x, y)
                        self.add_to_history('Addition', f"{x} + {y}", result)
                    elif choice == '2':
                        result = self.subtract(x, y)
                        self.add_to_history('Subtraction', f"{x} - {y}", result)
                    elif choice == '3':
                        result = self.multiply(x, y)
                        self.add_to_history('Multiplication', f"{x} × {y}", result)
                    elif choice == '4':
                        result = self.divide(x, y)
                        self.add_to_history('Division', f"{x} ÷ {y}", result)
                    elif choice == '5':
                        result = self.power(x, y)
                        self.add_to_history('Power', f"{x}^{y}", result)
                    elif choice == '7':
                        result = self.percentage(x, y)
                        self.add_to_history('Percentage', f"{x}% of {y}", result)
                    
                    print(f"\nResult: {result}")
                    input("\nPress Enter to continue...")

            except ValueError as e:
                print(f"\nError: {str(e)}")
                input("\nPress Enter to continue...")
            except Exception as e:
                print(f"\nAn unexpected error occurred: {str(e)}")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    calc = AdvancedCalculator()
    calc.run() 
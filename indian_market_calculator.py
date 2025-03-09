import math
import statistics
import datetime
import json
import os
from typing import List, Dict, Union, Optional
from decimal import Decimal, getcontext
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class IndianMarketCalculator:
    def __init__(self):
        self.history = []
        self.memory = {}
        self.load_history()
        self._setup_market_data()
        
    def _setup_market_data(self):
        """Setup Indian market specific data and constants"""
        # Key Interest Rates
        self.interest_rates = {
            'repo_rate': 6.50,  # RBI Repo Rate
            'reverse_repo_rate': 3.35,  # RBI Reverse Repo Rate
            'crr': 4.50,  # Cash Reserve Ratio
            'slr': 18.00,  # Statutory Liquidity Ratio
            'mclr': 8.50,  # Marginal Cost of Funds based Lending Rate
            'base_rate': 8.75,  # Base Rate
            'savings_rate': 3.50,  # Savings Account Rate
        }
        
        # Tax Rates for FY 2023-24
        self.tax_rates = {
            'gst': {
                'nil': 0,
                'low': 5,
                'medium': 12,
                'standard': 18,
                'high': 28
            },
            'income_tax': {
                'old_regime': [
                    (250000, 0),
                    (500000, 5),
                    (750000, 20),
                    (1000000, 30)
                ],
                'new_regime': [
                    (300000, 0),
                    (600000, 5),
                    (900000, 10),
                    (1200000, 15),
                    (1500000, 20),
                    (float('inf'), 30)
                ]
            }
        }
        
        # Currency conversion (example rates)
        self.forex_rates = {
            'USD_INR': 82.50,
            'EUR_INR': 89.75,
            'GBP_INR': 104.25,
            'JPY_INR': 0.55,
        }

    def calculate_income_tax(self, income: float, regime: str = 'new') -> Dict:
        """Calculate income tax based on selected regime"""
        tax_slabs = self.tax_rates['income_tax'][f'{regime}_regime']
        total_tax = 0
        tax_breakdown = []
        
        remaining_income = income
        previous_slab = 0
        
        for slab, rate in tax_slabs:
            if income > previous_slab:
                taxable_amount = min(income - previous_slab, slab - previous_slab)
                tax_amount = (taxable_amount * rate) / 100
                total_tax += tax_amount
                tax_breakdown.append({
                    'slab': f"₹{previous_slab:,} to ₹{slab:,}",
                    'rate': f"{rate}%",
                    'tax_amount': tax_amount
                })
            previous_slab = slab
            
        # Calculate cess (4% on total tax)
        cess = total_tax * 0.04
        
        return {
            'total_income': income,
            'regime': regime,
            'tax_breakdown': tax_breakdown,
            'total_tax': total_tax,
            'cess': cess,
            'final_tax': total_tax + cess
        }

    def calculate_gst(self, amount: float, rate_category: str) -> Dict:
        """Calculate GST for given amount and rate category"""
        if rate_category not in self.tax_rates['gst']:
            raise ValueError(f"Invalid GST rate category. Choose from {list(self.tax_rates['gst'].keys())}")
            
        rate = self.tax_rates['gst'][rate_category]
        gst_amount = (amount * rate) / 100
        
        return {
            'original_amount': amount,
            'rate': rate,
            'cgst': gst_amount / 2,
            'sgst': gst_amount / 2,
            'total_gst': gst_amount,
            'final_amount': amount + gst_amount
        }

    def calculate_loan_emi(self, principal: float, interest_rate: float, tenure_years: float) -> Dict:
        """Calculate loan EMI with Indian market rates"""
        monthly_rate = interest_rate / (12 * 100)
        tenure_months = tenure_years * 12
        
        emi = (principal * monthly_rate * (1 + monthly_rate)**tenure_months) / ((1 + monthly_rate)**tenure_months - 1)
        
        total_payment = emi * tenure_months
        total_interest = total_payment - principal
        
        return {
            'loan_amount': principal,
            'interest_rate': interest_rate,
            'tenure_years': tenure_years,
            'monthly_emi': emi,
            'total_interest': total_interest,
            'total_payment': total_payment
        }

    def calculate_fd_returns(self, principal: float, interest_rate: float, tenure_years: float) -> Dict:
        """Calculate Fixed Deposit returns"""
        amount = principal * (1 + interest_rate/100)**tenure_years
        interest_earned = amount - principal
        
        return {
            'principal': principal,
            'interest_rate': interest_rate,
            'tenure_years': tenure_years,
            'maturity_amount': amount,
            'interest_earned': interest_earned
        }

    def calculate_ppf_returns(self, yearly_investment: float, tenure_years: float = 15) -> Dict:
        """Calculate Public Provident Fund (PPF) returns"""
        ppf_rate = 7.1  # Current PPF interest rate
        total_investment = yearly_investment * tenure_years
        balance = 0
        yearly_breakdown = []
        
        for year in range(1, tenure_years + 1):
            interest = balance * (ppf_rate / 100)
            balance += yearly_investment + interest
            yearly_breakdown.append({
                'year': year,
                'investment': yearly_investment,
                'interest_earned': interest,
                'balance': balance
            })
            
        return {
            'yearly_investment': yearly_investment,
            'tenure_years': tenure_years,
            'total_investment': total_investment,
            'final_balance': balance,
            'total_interest': balance - total_investment,
            'yearly_breakdown': yearly_breakdown
        }

    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict:
        """Convert currency using stored forex rates"""
        if from_currency == to_currency:
            return {'original_amount': amount, 'converted_amount': amount}
            
        rate_key = f"{from_currency}_{to_currency}"
        if rate_key not in self.forex_rates:
            raise ValueError(f"Exchange rate not available for {from_currency} to {to_currency}")
            
        converted_amount = amount * self.forex_rates[rate_key]
        return {
            'original_amount': amount,
            'original_currency': from_currency,
            'converted_amount': converted_amount,
            'target_currency': to_currency,
            'exchange_rate': self.forex_rates[rate_key]
        }

    def calculate_sip_returns(self, monthly_investment: float, expected_return: float, tenure_years: float) -> Dict:
        """Calculate SIP (Systematic Investment Plan) returns"""
        monthly_rate = expected_return / (12 * 100)
        tenure_months = tenure_years * 12
        
        total_investment = monthly_investment * tenure_months
        
        # Calculate future value using SIP formula
        amount = monthly_investment * ((1 + monthly_rate) * ((1 + monthly_rate)**tenure_months - 1) / monthly_rate)
        
        return {
            'monthly_investment': monthly_investment,
            'expected_return_rate': expected_return,
            'tenure_years': tenure_years,
            'total_investment': total_investment,
            'final_amount': amount,
            'wealth_gained': amount - total_investment
        }

    def calculate_nps_returns(self, monthly_investment: float, equity_ratio: float, 
                            expected_equity_return: float, expected_debt_return: float, 
                            tenure_years: float) -> Dict:
        """Calculate National Pension System (NPS) returns"""
        if not 0 <= equity_ratio <= 75:
            raise ValueError("Equity ratio must be between 0 and 75%")
            
        debt_ratio = 100 - equity_ratio
        monthly_equity = monthly_investment * (equity_ratio / 100)
        monthly_debt = monthly_investment * (debt_ratio / 100)
        
        total_investment = monthly_investment * 12 * tenure_years
        
        # Calculate returns for equity and debt portions
        equity_returns = self.calculate_sip_returns(monthly_equity, expected_equity_return, tenure_years)
        debt_returns = self.calculate_sip_returns(monthly_debt, expected_debt_return, tenure_years)
        
        final_amount = equity_returns['final_amount'] + debt_returns['final_amount']
        
        return {
            'monthly_investment': monthly_investment,
            'equity_ratio': equity_ratio,
            'debt_ratio': debt_ratio,
            'tenure_years': tenure_years,
            'total_investment': total_investment,
            'final_amount': final_amount,
            'wealth_gained': final_amount - total_investment,
            'equity_component': equity_returns['final_amount'],
            'debt_component': debt_returns['final_amount']
        }

    def display_menu(self):
        """Display the calculator menu"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        menu = """
╔══════════════════════════════════════════════════════╗
║            INDIAN MARKET CALCULATOR 2024             ║
╚══════════════════════════════════════════════════════╝

═══════════════════ TAX CALCULATIONS ══════════════════
1.  Calculate Income Tax (Old & New Regime)
2.  Calculate GST
3.  Professional Tax Calculator

══════════════════ INVESTMENT ANALYSIS ═════════════════
4.  SIP Returns Calculator
5.  Fixed Deposit Calculator
6.  PPF Calculator
7.  NPS Calculator
8.  Mutual Fund Returns Calculator

═════════════════ LOAN & EMI ANALYSIS ═════════════════
9.  Home Loan EMI Calculator
10. Personal Loan EMI Calculator
11. Car Loan EMI Calculator
12. Loan Comparison Tool

════════════════════ MARKET METRICS ══════════════════
13. Current Market Indicators
14. Interest Rate Information
15. Currency Conversion
16. Stock Analysis Tools

═══════════════════ RETIREMENT PLANNING ═══════════════
17. Retirement Corpus Calculator
18. Pension Planning Calculator
19. Goal-based Investment Planning

════════════════════ OTHER OPTIONS ══════════════════
20. View Calculation History
21. Export Calculations to Excel
22. Market Updates & News
23. Exit

Enter your choice (1-23): """
        print(menu)

    def run(self):
        """Main calculator loop"""
        while True:
            self.display_menu()
            
            try:
                choice = input("\nEnter your choice (1-23): ").strip()
                
                if choice == '23':  # Exit
                    print("\nThank you for using Indian Market Calculator!")
                    break

                # Tax Calculations
                if choice == '1':
                    income = float(input("Enter annual income: ₹"))
                    regime = input("Enter tax regime (old/new): ").lower()
                    result = self.calculate_income_tax(income, regime)
                    self._display_tax_calculation(result)

                elif choice == '2':
                    amount = float(input("Enter amount: ₹"))
                    print("\nGST Categories:")
                    print("nil (0%), low (5%), medium (12%), standard (18%), high (28%)")
                    category = input("Enter GST category: ").lower()
                    result = self.calculate_gst(amount, category)
                    self._display_gst_calculation(result)

                # Investment Calculations
                elif choice == '4':
                    monthly_inv = float(input("Enter monthly SIP amount: ₹"))
                    returns = float(input("Enter expected annual returns (%): "))
                    years = float(input("Enter investment period (years): "))
                    result = self.calculate_sip_returns(monthly_inv, returns, years)
                    self._display_sip_calculation(result)

                elif choice == '5':
                    principal = float(input("Enter FD amount: ₹"))
                    rate = float(input("Enter interest rate (%): "))
                    years = float(input("Enter tenure (years): "))
                    result = self.calculate_fd_returns(principal, rate, years)
                    self._display_fd_calculation(result)

                # Loan Calculations
                elif choice in ['9', '10', '11']:
                    principal = float(input("Enter loan amount: ₹"))
                    rate = float(input("Enter interest rate (%): "))
                    years = float(input("Enter loan tenure (years): "))
                    result = self.calculate_loan_emi(principal, rate, years)
                    self._display_loan_calculation(result)

                # Market Information
                elif choice == '13':
                    self._display_market_indicators()

                elif choice == '14':
                    self._display_interest_rates()

                elif choice == '15':
                    amount = float(input("Enter amount: "))
                    from_curr = input("Enter source currency (e.g., USD): ").upper()
                    to_curr = input("Enter target currency (e.g., INR): ").upper()
                    result = self.convert_currency(amount, from_curr, to_curr)
                    self._display_currency_conversion(result)

                elif choice == '20':
                    self._display_history()

                elif choice == '21':
                    self._export_to_excel()

                else:
                    print("\nThis feature is under development.")

            except ValueError as e:
                print(f"\nError: {str(e)}")
            except Exception as e:
                print(f"\nAn unexpected error occurred: {str(e)}")
            
            input("\nPress Enter to continue...")

    def _display_tax_calculation(self, result: Dict):
        """Display formatted tax calculation results"""
        print("\n═══════════════════ TAX CALCULATION SUMMARY ═══════════════════")
        print(f"Total Income: ₹{result['total_income']:,.2f}")
        print(f"Tax Regime: {result['regime'].upper()}")
        print("\nTax Breakdown:")
        for slab in result['tax_breakdown']:
            print(f"  {slab['slab']}: {slab['rate']} = ₹{slab['tax_amount']:,.2f}")
        print(f"\nTotal Tax: ₹{result['total_tax']:,.2f}")
        print(f"Health & Education Cess (4%): ₹{result['cess']:,.2f}")
        print(f"Final Tax Liability: ₹{result['final_tax']:,.2f}")

    def _display_gst_calculation(self, result: Dict):
        """Display formatted GST calculation results"""
        print("\n═══════════════════ GST CALCULATION SUMMARY ═══════════════════")
        print(f"Original Amount: ₹{result['original_amount']:,.2f}")
        print(f"GST Rate: {result['rate']}%")
        print(f"CGST (50%): ₹{result['cgst']:,.2f}")
        print(f"SGST (50%): ₹{result['sgst']:,.2f}")
        print(f"Total GST: ₹{result['total_gst']:,.2f}")
        print(f"Final Amount: ₹{result['final_amount']:,.2f}")

    def _display_sip_calculation(self, result: Dict):
        """Display formatted SIP calculation results"""
        print("\n═══════════════════ SIP CALCULATION SUMMARY ═══════════════════")
        print(f"Monthly Investment: ₹{result['monthly_investment']:,.2f}")
        print(f"Investment Period: {result['tenure_years']} years")
        print(f"Expected Return Rate: {result['expected_return_rate']}%")
        print(f"Total Investment: ₹{result['total_investment']:,.2f}")
        print(f"Final Amount: ₹{result['final_amount']:,.2f}")
        print(f"Wealth Gained: ₹{result['wealth_gained']:,.2f}")

    def _display_fd_calculation(self, result: Dict):
        """Display formatted FD calculation results"""
        print("\n═══════════════════ FD CALCULATION SUMMARY ═══════════════════")
        print(f"Principal Amount: ₹{result['principal']:,.2f}")
        print(f"Interest Rate: {result['interest_rate']}%")
        print(f"Tenure: {result['tenure_years']} years")
        print(f"Maturity Amount: ₹{result['maturity_amount']:,.2f}")
        print(f"Interest Earned: ₹{result['interest_earned']:,.2f}")

    def _display_loan_calculation(self, result: Dict):
        """Display formatted loan calculation results"""
        print("\n═══════════════════ LOAN CALCULATION SUMMARY ═══════════════════")
        print(f"Loan Amount: ₹{result['loan_amount']:,.2f}")
        print(f"Interest Rate: {result['interest_rate']}%")
        print(f"Tenure: {result['tenure_years']} years")
        print(f"Monthly EMI: ₹{result['monthly_emi']:,.2f}")
        print(f"Total Interest: ₹{result['total_interest']:,.2f}")
        print(f"Total Payment: ₹{result['total_payment']:,.2f}")

    def _display_market_indicators(self):
        """Display current market indicators"""
        print("\n═══════════════════ MARKET INDICATORS ═══════════════════")
        print("Key Interest Rates:")
        for rate_name, rate_value in self.interest_rates.items():
            print(f"  {rate_name.replace('_', ' ').title()}: {rate_value}%")

    def _display_interest_rates(self):
        """Display current interest rates"""
        print("\n═══════════════════ CURRENT INTEREST RATES ═══════════════════")
        for rate_name, rate_value in self.interest_rates.items():
            print(f"{rate_name.replace('_', ' ').title()}: {rate_value}%")

    def _display_currency_conversion(self, result: Dict):
        """Display formatted currency conversion results"""
        print("\n═══════════════════ CURRENCY CONVERSION ═══════════════════")
        print(f"Original Amount: {result['original_currency']} {result['original_amount']:,.2f}")
        print(f"Exchange Rate: 1 {result['original_currency']} = {result['exchange_rate']} {result['target_currency']}")
        print(f"Converted Amount: {result['target_currency']} {result['converted_amount']:,.2f}")

    def _display_history(self):
        """Display calculation history"""
        print("\n═══════════════════ CALCULATION HISTORY ═══════════════════")
        for entry in self.history:
            print(f"[{entry['timestamp']}] {entry['operation']}: {entry['details']}")

    def _export_to_excel(self):
        """Export calculation history to Excel"""
        try:
            df = pd.DataFrame(self.history)
            filename = f"calculation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            print(f"\nHistory exported to {filename}")
        except Exception as e:
            print(f"\nError exporting to Excel: {str(e)}")

if __name__ == "__main__":
    calc = IndianMarketCalculator()
    calc.run() 
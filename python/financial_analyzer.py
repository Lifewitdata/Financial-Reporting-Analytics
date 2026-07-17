#!/usr/bin/env python3
"""
Financial Analyzer Main Module
This module serves as the main entry point for the financial reporting and analytics system,
integrating data cleaning, reconciliation, KPI reporting, and financial statement generation.
"""

import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

# Import our custom modules
from data_cleaning import FinancialDataCleaner
from reconciliation import FinancialReconciliation
from kpi_report import KPIReporter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    def __init__(self, data_dir='data'):
        """
        Initialize the financial analyzer

        Args:
            data_dir (str): Directory containing the data files
        """
        self.data_dir = data_dir
        self.data_cleaner = FinancialDataCleaner(data_dir)
        self.reconciler = FinancialReconciliation(data_dir)
        self.kpi_reporter = KPIReporter(data_dir)
        self.data = {}

        # Initialize data
        self.load_financial_data()

    def load_financial_data(self):
        """Load essential financial data for analysis"""
        logger.info("Loading financial data...")
        self.data = self.data_cleaner.load_all_data()
        logger.info(f"Loaded {len(self.data)} datasets")
        return self.data

    def generate_financial_statements(self, fiscal_year=None, fiscal_period=None):
        """
        Generate core financial statements (Income Statement, Balance Sheet, Cash Flow)

        Args:
            fiscal_year (int, optional): Filter by fiscal year
            fiscal_period (int, optional): Filter by fiscal period

        Returns:
            dict: Dictionary containing financial statements
        """
        print("=== Generating Financial Statements ===")

        if 'financial_transactions' not in self.data or 'chart_of_accounts' not in self.data:
            self.load_financial_data()

        # Filter data by period if specified
        transactions = self.data['financial_transactions'].copy()
        if fiscal_year is not None:
            if fiscal_period is not None:
                transactions = transactions[
                    (transactions['fiscal_year'] == fiscal_year) &
                    (transactions['fiscal_period'] == fiscal_period)
                ]
            else:
                transactions = transactions[transactions['fiscal_year'] == fiscal_year]

        # Join with chart of accounts
        transactions = transactions.merge(
            self.data['chart_of_accounts'][['account_id', 'account_category', 'account_type']],
            on='account_id',
            how='left'
        )

        # Income Statement
        revenue = transactions[transactions['account_category'] == 'Operating Revenue']['amount'].sum()
        cogs = transactions[transactions['account_category'] == 'COGS']['amount'].sum()
        operating_expenses = transactions[transactions['account_category'] == 'Operating Expense']['amount'].sum()
        non_op_revenue = transactions[transactions['account_category'] == 'Non-Operating Revenue']['amount'].sum()
        non_op_expense = transactions[transactions['account_category'] == 'Non-Operating Expense']['amount'].sum()

        gross_profit = revenue - cogs
        operating_income = gross_profit - operating_expenses
        net_income = operating_income + non_op_revenue - non_op_expense

        income_statement = {
            'revenue': revenue,
            'cost_of_goods_sold': cogs,
            'gross_profit': gross_profit,
            'operating_expenses': operating_expenses,
            'operating_income': operating_income,
            'non_operating_revenue': non_op_revenue,
            'non_operating_expense': non_op_expense,
            'net_income': net_income
        }

        # Balance Sheet (based on cumulative account balances)
        # Get all transactions up to the period
        if fiscal_year is not None and fiscal_period is not None:
            # For a specific period, we want all transactions up to that point
            # This is a simplified approach - in practice, you'd want to calculate running balances
            cutoff_transactions = self.data['financial_transactions'][
                (self.data['financial_transactions']['fiscal_year'] < fiscal_year) |
                ((self.data['financial_transactions']['fiscal_year'] == fiscal_year) &
                 (self.data['financial_transactions']['fiscal_period'] <= fiscal_period))
            ].copy()
        else:
            # All time
            cutoff_transactions = self.data['financial_transactions'].copy()

        # Calculate account balances
        account_balances = cutoff_transactions.groupby('account_id')['amount'].sum().reset_index()
        account_balances = account_balances.merge(
            self.data['chart_of_accounts'][['account_id', 'account_category']],
            on='account_id',
            how='left'
        )

        # Group by account category
        balance_sheet = {}
        for category in ['Asset', 'Liability', 'Equity']:
            category_balance = account_balances[account_balances['account_category'] == category]['amount'].sum()
            balance_sheet[category.lower() + 's'] = category_balance

        # Cash Flow Statement (simplified indirect method)
        # Operating cash flow = Net income + non-cash expenses - changes in working capital
        # For simplicity, we'll use net income as a proxy and adjust for major non-cash items
        depreciation = transactions[transactions['account_id'] == '1550']['amount'].abs().sum()  # Accumulated depreciation

        operating_cash_flow = net_income + depreciation  # Simplified

        # Investing activities (changes in long-term assets)
        # For simplicity, we'll look at equipment account changes
        equipment_change = abs(
            cutoff_transactions[cutoff_transactions['account_id'] == '1500']['amount'].sum() -
            self.data['financial_transactions'][
                self.data['financial_transactions']['account_id'] == '1500'
            ]['amount'].sum() if len(self.data['financial_transactions']) > 0 else 0
        )

        investing_cash_flow = -equipment_change  # Negative for capital expenditures

        # Financing activities (debt and equity changes)
        # Simplified: look at long-term debt and equity accounts
        debt_change = abs(
            cutoff_transactions[cutoff_transactions['account_id'] == '2500']['amount'].sum() -
            self.data['financial_transactions'][
                self.data['financial_transactions']['account_id'] == '2500'
            ]['amount'].sum() if len(self.data['financial_transactions']) > 0 else 0
        )

        equity_change = abs(
            cutoff_transactions[cutoff_transactions['account_id'] == '3000']['amount'].sum() -
            self.data['financial_transactions'][
                self.data['financial_transactions']['account_id'] == '3000'
            ]['amount'].sum() if len(self.data['financial_transactions']) > 0 else 0
        )

        financing_cash_flow = debt_change + equity_change  # Simplified

        cash_flow_statement = {
            'operating_cash_flow': operating_cash_flow,
            'investing_cash_flow': investing_cash_flow,
            'financing_cash_flow': financing_cash_flow,
            'net_change_in_cash': operating_cash_flow + investing_cash_flow + financing_cash_flow
        }

        statements = {
            'income_statement': income_statement,
            'balance_sheet': balance_sheet,
            'cash_flow_statement': cash_flow_statement
        }

        return statements

    def print_financial_statements(self, fiscal_year=None, fiscal_period=None):
        """Print formatted financial statements to console"""
        statements = self.generate_financial_statements(fiscal_year, fiscal_period)

        period_desc = ""
        if fiscal_year and fiscal_period:
            period_desc = f" for FY{fiscal_year} Period {fiscal_period}"
        elif fiscal_year:
            period_desc = f" for FY{fiscal_year}"

        print(f"\nFINANCIAL STATEMENTS{period_desc}")
        print("=" * 50)

        # Income Statement
        print("\nINCOME STATEMENT")
        print("-" * 30)
        is_data = statements['income_statement']
        print(f"Revenue:                           ${is_data['revenue']:>12,.2f}")
        print(f"Cost of Goods Sold:                ${is_data['cost_of_goods_sold']:>12,.2f}")
        print(f"Gross Profit:                      ${is_data['gross_profit']:>12,.2f}")
        print(f"Operating Expenses:                ${is_data['operating_expenses']:>12,.2f}")
        print(f"Operating Income:                  ${is_data['operating_income']:>12,.2f}")
        print(f"Non-operating Income:              ${is_data['non_operating_revenue']:>12,.2f}")
        print(f"Non-operating Expenses:            ${is_data['non_operating_expense']:>12,.2f}")
        print(f"Net Income:                        ${is_data['net_income']:>12,.2f}")

        # Balance Sheet
        print("\nBALANCE SHEET")
        print("-" * 30)
        bs_data = statements['balance_sheet']
        print(f"Assets:                            ${bs_data['assets']:>12,.2f}")
        print(f"Liabilities:                       ${bs_data['liabilities']:>12,.2f}")
        print(f"Equity:                            ${bs_data['equity']:>12,.2f}")

        # Check if balance sheet balances
        assets = bs_data['assets']
        liabilities_equity = bs_data['liabilities'] + bs_data['equity']
        balance_diff = assets - liabilities_equity
        print(f"\nBalance Check:                     ${balance_diff:>12,.2f}")
        if abs(balance_diff) < 0.01:
            print("✓ BALANCE SHEET IS IN BALANCE")
        else:
            print("✗ BALANCE SHEET IS OUT OF BALANCE")

        # Cash Flow Statement
        print("\nCASH FLOW STATEMENT")
        print("-" * 30)
        cf_data = statements['cash_flow_statement']
        print(f"Operating Cash Flow:               ${cf_data['operating_cash_flow']:>12,.2f}")
        print(f"Investing Cash Flow:               ${cf_data['investing_cash_flow']:>12,.2f}")
        print(f"Financing Cash Flow:               ${cf_data['financing_cash_flow']:>12,.2f}")
        print(f"Net Change in Cash:                ${cf_data['net_change_in_cash']:>12,.2f}")

    def generate_kpi_report(self, fiscal_year=None, fiscal_period=None, output_dir='outputs'):
        """
        Generate KPI report using the KPI reporter

        Args:
            fiscal_year (int, optional): Filter by fiscal year
            fiscal_period (int, optional): Filter by fiscal period
            output_dir (str): Directory to save the report

        Returns:
            str: Path to the generated report
        """
        return self.kpi_reporter.generate_kpi_report(fiscal_year, fiscal_period, output_dir)

    def perform_bank_reconciliation(self, bank_statement_df, gl_account_cash='1000'):
        """
        Perform bank reconciliation

        Args:
            bank_statement_df (DataFrame): Bank statement data
            gl_account_cash (str): GL account code for cash

        Returns:
            dict: Reconciliation results
        """
        # Ensure we have financial data loaded
        if 'financial_transactions' not in self.data:
            self.load_financial_data()

        return self.reconciler.bank_reconciliation(bank_statement_df, gl_account_cash)

    def clean_data(self):
        """Perform data cleaning on all loaded data"""
        print("=== Performing Data Cleaning ===")

        # Clean transactions data
        if 'financial_transactions' in self.data:
            self.data['financial_transactions_clean'] = self.data_cleaner.clean_transactions_data()

        # Clean chart of accounts
        if 'chart_of_accounts' in self.data:
            self.data['chart_of_accounts_clean'] = self.data_cleaner.clean_chart_of_accounts()

        # Validate fiscal periods
        if 'financial_transactions' in self.data and 'fiscal_calendar' in self.data:
            mismatches = self.data_cleaner.validate_fiscal_periods()
            if len(mismatches) > 0:
                print(f"Warning: Found {len(mismatches)} fiscal period mismatches")
            else:
                print("✓ No fiscal period mismatches found")

        # Generate data quality report
        quality_report = self.data_cleaner.generate_data_quality_report()
        print("\nData Quality Summary:")
        for dataset, info in quality_report.items():
            print(f"  {dataset}: {info['rows']} rows, {info['missing_values']} missing values")

    def save_cleaned_data(self, output_dir='data/cleaned'):
        """Save cleaned data to CSV files"""
        self.data_cleaner.save_cleaned_data(output_dir)

def main():
    """Main function to demonstrate the financial analyzer"""
    print("Financial Reporting and Analytics System")
    print("=" * 50)

    # Initialize analyzer
    analyzer = FinancialAnalyzer()

    # Demonstrate data cleaning
    analyzer.clean_data()

    # Generate financial statements for different periods
    print("\n1. Generating Q1 2024 Financial Statements:")
    analyzer.print_financial_statements(fiscal_year=2024, fiscal_period=1)

    print("\n2. Generating Full Year 2024 Financial Statements:")
    analyzer.print_financial_statements(fiscal_year=2024)

    print("\n3. Generating All-Time Financial Statements:")
    analyzer.print_financial_statements()

    # Generate KPI report
    print("\n4. Generating KPI Report:")
    kpi_report_path = analyzer.generate_kpi_report(fiscal_year=2024, fiscal_period=1)
    print(f"   KPI report saved to: {kpi_report_path}")

    # Save cleaned data
    print("\n5. Saving Cleaned Data:")
    analyzer.save_cleaned_data()

    print("\nDemo completed!")

if __name__ == "__main__":
    main()
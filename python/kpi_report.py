#!/usr/bin/env python3
"""
KPI Reporting Module
This module calculates and reports key performance indicators for financial analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KPIReporter:
    def __init__(self, data_dir='data'):
        """
        Initialize the KPI reporter
        """
        self.data_dir = data_dir
        self.data = {}

    def load_data(self, filename):
        """
        Load a CSV file and store it in the data dictionary
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            df = pd.read_csv(filepath)
            # Convert date columns
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            self.data[filename.split('.')[0]] = df
            logger.info(f"Loaded {filename}: {df.shape[0]} rows")
            return df
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return None

    def load_financial_data(self):
        """
        Load essential financial data for KPI calculations
        """
        required_files = [
            'financial_transactions.csv',
            'chart_of_accounts.csv',
            'departments.csv',
            'fiscal_calendar.csv'
        ]

        for file in required_files:
            self.load_data(file)

        return self.data

    def calculate_profitability_kpis(self, fiscal_year=None, fiscal_period=None):
        """
        Calculate profitability KPIs
        """
        print("=== Calculating Profitability KPIs ===")

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

        # Calculate revenue and expense components
        revenue = transactions[transactions['account_category'] == 'Operating Revenue']['amount'].sum()
        cogs = transactions[transactions['account_category'] == 'COGS']['amount'].sum()
        operating_expenses = transactions[transactions['account_category'] == 'Operating Expense']['amount'].sum()
        non_op_revenue = transactions[transactions['account_category'] == 'Non-Operating Revenue']['amount'].sum()
        non_op_expense = transactions[transactions['account_category'] == 'Non-Operating Expense']['amount'].sum()

        # Calculate KPIs
        gross_profit = revenue - cogs
        operating_income = gross_profit - operating_expenses
        net_income = operating_income + non_op_revenue - non_op_expense

        kpis = {}

        # Profitability Ratios
        if revenue != 0:
            kpis['gross_profit_margin'] = (gross_profit / revenue) * 100
            kpis['operating_profit_margin'] = (operating_income / revenue) * 100
            kpis['net_profit_margin'] = (net_income / revenue) * 100
        else:
            kpis['gross_profit_margin'] = 0
            kpis['operating_profit_margin'] = 0
            kpis['net_profit_margin'] = 0

        # Return on metrics (simplified - would need average assets/equity)
        kpis['gross_profit'] = gross_profit
        kpis['operating_income'] = operating_income
        kpis['net_income'] = net_income
        kpis['revenue'] = revenue
        kpis['cogs'] = cogs
        kpis['operating_expenses'] = operating_expenses

        return kpis

    def calculate_efficiency_kpis(self, fiscal_year=None, fiscal_period=None):
        """
        Calculate efficiency KPIs
        """
        print("=== Calculating Efficiency KPIs ===")

        if 'financial_transactions' not in self.data:
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

        kpis = {}

        # Expense ratios
        total_expenses = transactions[transactions['amount'] < 0]['amount'].abs().sum()
        operating_expenses = transactions[
            (transactions['amount'] < 0) &
            (transactions['account_category'] == 'Operating Expense')
        ]['amount'].abs().sum()

        if total_expenses != 0:
            kpis['operating_expense_ratio'] = (operating_expenses / total_expenses) * 100
        else:
            kpis['operating_expense_ratio'] = 0

        # Department expense analysis
        if 'departments' in self.data:
            dept_expenses = transactions[
                transactions['account_category'] == 'Operating Expense'
            ].merge(
                self.data['departments'][['department_id', 'department_name']],
                on='department_id',
                how='left'
            ).groupby('department_name')['amount'].abs().sum().reset_index()

            dept_expenses = dept_expenses.sort_values('amount', ascending=False)
            kpis['department_expenses'] = dept_expenses

            # Top expense department
            if len(dept_expenses) > 0:
                kpis['top_expense_department'] = dept_expenses.iloc[0]['department_name']
                kpis['top_expense_amount'] = dept_expenses.iloc[0]['amount']
            else:
                kpis['top_expense_department'] = None
                kpis['top_expense_amount'] = 0

        return kpis

    def calculate_liquidity_kpis(self):
        """
        Calculate liquidity KPIs (based on balance sheet)
        """
        print("=== Calculating Liquidity KPIs ===")

        if 'financial_transactions' not in self.data or 'chart_of_accounts' not in self.data:
            self.load_financial_data()

        # Calculate cumulative balances for current period (YTD)
        transactions = self.data['financial_transactions'].copy()

        # Get latest period
        latest_year = transactions['fiscal_year'].max()
        latest_period = transactions[transactions['fiscal_year'] == latest_year]['fiscal_period'].max()

        # Get YTD transactions
        ytd_transactions = transactions[
            (transactions['fiscal_year'] < latest_year) |
            ((transactions['fiscal_year'] == latest_year) &
             (transactions['fiscal_period'] <= latest_period))
        ]

        # Calculate account balances
        account_balances = ytd_transactions.groupby('account_id')['amount'].sum().reset_index()
        account_balances = account_balances.merge(
            self.data['chart_of_accounts'][['account_id', 'account_category']],
            on='account_id',
            how='left'
        )

        kpis = {}

        # Current Assets
        current_assets = account_balances[
            account_balances['account_category'] == 'Current Asset'
        ]['amount'].sum()

        # Current Liabilities
        current_liabilities = account_balances[
            account_balances['account_category'] == 'Current Liability'
        ]['amount'].abs().sum()  # Liabilities are typically negative

        # Cash and equivalents (simplified)
        cash_accounts = account_balances[
            account_balances['account_id'].isin(['1000', '1010'])  # Cash and AR
        ]['amount'].sum()

        # Liquidity ratios
        if current_liabilities != 0:
            kpis['current_ratio'] = current_assets / current_liabilities
        else:
            kpis['current_ratio'] = float('inf')

        if current_liabilities != 0:
            kpis['quick_ratio'] = cash_accounts / current_liabilities  # Simplified quick ratio
        else:
            kpis['quick_ratio'] = float('inf')

        kpis['current_assets'] = current_assets
        kpis['current_liabilities'] = current_liabilities
        kpis['cash_and_equivalents'] = cash_accounts

        return kpis

    def calculate_activity_kpis(self, fiscal_year=None):
        """
        Calculate activity/turnover KPIs
        """
        print("=== Calculating Activity KPIs ===")

        if 'financial_transactions' not in self.data or 'chart_of_accounts' not in self.data:
            self.load_financial_data()

        # Filter data for the year
        transactions = self.data['financial_transactions'].copy()
        if fiscal_year is not None:
            transactions = transactions[transactions['fiscal_year'] == fiscal_year]

        kpis = {}

        # Revenue (for turnover ratios)
        revenue = transactions[
            transactions['account_category'] == 'Operating Revenue'
        ]['amount'].sum()

        # Average receivables (simplified - would need beginning and ending balances)
        ar_balance = transactions[
            transactions['account_id'] == '1010'  # Accounts Receivable
        ]['amount'].sum()

        # Average inventory (simplified)
        inventory_balance = transactions[
            transactions['account_id'] == '1020'  # Inventory
        ]['amount'].sum()

        # Turnover ratios
        if ar_balance != 0:
            kpis['receivables_turnover'] = revenue / ar_balance
            kpis['days_sales_outstanding'] = 365 / kpis['receivables_turnover'] if kpis['receivables_turnover'] != 0 else 0
        else:
            kpis['receivables_turnover'] = 0
            kpis['days_sales_outstanding'] = 0

        if inventory_balance != 0:
            cogs = transactions[
                transactions['account_category'] == 'COGS'
            ]['amount'].sum()
            kpis['inventory_turnover'] = cogs / inventory_balance
            kpis['days_inventory_outstanding'] = 365 / kpis['inventory_turnover'] if kpis['inventory_turnover'] != 0 else 0
        else:
            kpis['inventory_turnover'] = 0
            kpis['days_inventory_outstanding'] = 0

        kpis['revenue'] = revenue
        kpis['ar_balance'] = ar_balance
        kpis['inventory_balance'] = inventory_balance

        return kpis

    def generate_kpi_report(self, fiscal_year=None, fiscal_period=None, output_dir='outputs'):
        """
        Generate a comprehensive KPI report
        """
        print("Generating KPI Report...")
        print("=" * 40)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Calculate all KPI categories
        profitability_kpis = self.calculate_profitability_kpis(fiscal_year, fiscal_period)
        efficiency_kpis = self.calculate_efficiency_kpis(fiscal_year, fiscal_period)
        liquidity_kpis = self.calculate_liquidity_kpis()
        activity_kpis = self.calculate_activity_kpis(fiscal_year)

        # Create report
        report_lines = []
        report_lines.append("KEY PERFORMANCE INDICATORS REPORT")
        report_lines.append("=" * 50)

        period_desc = ""
        if fiscal_year and fiscal_period:
            period_desc = f" for FY{fiscal_year} Period {fiscal_period}"
        elif fiscal_year:
            period_desc = f" for FY{fiscal_year}"
        else:
            period_desc = " (All Periods)"

        report_lines.append(f"Period:{period_desc}")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Profitability KPIs
        report_lines.append("PROFITABILITY KPIS")
        report_lines.append("-" * 30)
        for kpi, value in profitability_kpis.items():
            if isinstance(value, float):
                if 'margin' in kpi or 'ratio' in kpi:
                    report_lines.append(f"{kpi.replace('_', ' ').title():<30}: {value:>8.2f}%")
                else:
                    report_lines.append(f"{kpi.replace('_', ' ').title():<30}: ${value:>10,.2f}")
            else:
                report_lines.append(f"{kpi.replace('_', ' ').title():<30}: {value}")
        report_lines.append("")

        # Efficiency KPIs
        report_lines.append("EFFICIENCY KPIS")
        report_lines.append("-" * 30)
        for kpi, value in efficiency_kpis.items():
            if isinstance(value, float):
                if 'ratio' in kpi:
                    report_lines.append(f"{kpi.replace('_', ' ').title():<30}: {value:>8.2f}%")
                else:
                    report_lines.append(f"{kpi.replace('_', ' ').title():<30}: ${value:>10,.2f}")
            elif isinstance(value, pd.DataFrame):
                report_lines.append(f"{kpi.replace('_', ' ').title()}:")
                report_lines.append(value.to_string(index=False))
                report_lines.append("")
            else:
                report_lines.append(f"{kpi.replace('_', ' ').title():<30}: {value}")
        report_lines.append("")

        # Liquidity KPIs
        report_lines.append("LIQUIDITY KPIS")
        report_lines.append("-" * 30)
        for kpi, value in liquidity_kpis.items():
            if isinstance(value, float):
                if 'ratio' in kpi:
                    report_lines.append(f"{kpi.replace('_', ' ').title():<30}: {value:>8.2f}")
                else:
                    report_lines.append(f"{kpi.replace('_', ' ').title():<30}: ${value:>10,.2f}")
            else:
                report_lines.append(f"{kpi.replace('_', ' ').title():<30}: {value}")
        report_lines.append("")

        # Activity KPIs
        report_lines.append("ACTIVITY KPIS")
        report_lines.append("-" * 30)
        for kpi, value in activity_kpis.items():
            if isinstance(value, float):
                if 'turnover' in kpi or 'days' in kpi:
                    report_lines.append(f"{kpi.replace('_', ' ').title():<30}: {value:>8.2f}")
                else:
                    report_lines.append(f"{kpi.replace('_', ' ').title():<30}: ${value:>10,.2f}")
            else:
                report_lines.append(f"{kpi.replace('_', ' ').title():<30}: {value}")
        report_lines.append("")

        # Write report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if fiscal_year and fiscal_period:
            filename = f"kpi_report_fy{fiscal_year}_p{fiscal_period}_{timestamp}.txt"
        elif fiscal_year:
            filename = f"kpi_report_fy{fiscal_year}_{timestamp}.txt"
        else:
            filename = f"kpi_report_all_{timestamp}.txt"

        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w') as f:
            f.write('\n'.join(report_lines))

        print(f"KPI report saved to: {filepath}")

        # Also print to console
        print('\n'.join(report_lines))

        return filepath

def main():
    """
    Main function to demonstrate KPI reporting functionality
    """
    print("Financial KPI Reporting Demo")
    print("=" * 30)

    # Initialize KPI reporter
    kpi_reporter = KPIReporter()

    # Load financial data
    print("\nLoading financial data...")
    kpi_reporter.load_financial_data()

    # Generate KPI reports for different periods
    print("\n1. Generating Q1 2024 KPI Report:")
    kpi_reporter.generate_kpi_report(fiscal_year=2024, fiscal_period=1)

    print("\n2. Generating Full Year 2024 KPI Report:")
    kpi_reporter.generate_kpi_report(fiscal_year=2024)

    print("\n3. Generating All-Time KPI Report:")
    kpi_reporter.generate_kpi_report()

    print("\nDemo completed!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Financial Reconciliation Module
This module provides tools for reconciling financial data, particularly
bank reconciliations and intercompany reconciliations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialReconciliation:
    def __init__(self, data_dir='data'):
        """
        Initialize the reconciliation module
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
        Load essential financial data for reconciliation
        """
        required_files = [
            'financial_transactions.csv',
            'chart_of_accounts.csv',
            'departments.csv'
        ]

        for file in required_files:
            self.load_data(file)

        return self.data

    def bank_reconciliation(self, bank_statement_df, gl_account_cash='1000'):
        """
        Perform bank reconciliation between bank statement and general ledger
        """
        print("=== Bank Reconciliation Process ===")

        # Load GL cash account transactions
        if 'financial_transactions' not in self.data:
            self.load_financial_data()

        gl_transactions = self.data['financial_transactions'].copy()

        # Filter for cash account
        gl_cash = gl_transactions[gl_transactions['account_id'] == gl_account_cash].copy()
        print(f"GL Cash Account ({gl_account_cash}) Transactions: {len(gl_cash)} records")

        if len(gl_cash) == 0:
            print("ERROR: No transactions found for cash account")
            return None

        # Prepare bank statement data
        bank_stmt = bank_statement_df.copy()
        print(f"Bank Statement Transactions: {len(bank_stmt)} records")

        # Standardize column names for comparison
        # Assume bank statement has: date, description, amount, reference
        required_bank_cols = ['date', 'description', 'amount']
        missing_cols = [col for col in required_bank_cols if col not in bank_stmt.columns]
        if missing_cols:
            print(f"ERROR: Bank statement missing required columns: {missing_cols}")
            return None

        # Ensure amount is numeric
        bank_stmt['amount'] = pd.to_numeric(bank_stmt['amount'], errors='coerce')
        bank_stmt['amount'] = bank_stmt['amount'].fillna(0)

        # Prepare GL data for matching
        gl_cash = gl_cash.rename(columns={
            'transaction_date': 'date',
            'description': 'description',
            'amount': 'amount'
        })

        # Add transaction type identifiers
        gl_cash['source'] = 'GL'
        bank_stmt['source'] = 'Bank'

        # Create matching keys
        # Round amounts to 2 decimal places for comparison
        gl_cash['amount_rounded'] = (gl_cash['amount'] * 100).round() / 100
        bank_stmt['amount_rounded'] = (bank_stmt['amount'] * 100).round() / 100

        # Create composite key for matching
        gl_cash['match_key'] = (
            gl_cash['date'].dt.strftime('%Y-%m-%d') + '|' +
            gl_cash['amount_rounded'].astype(str) + '|' +
            gl_cash['description'].str[:20].str.upper().str.strip()
        )

        bank_stmt['match_key'] = (
            bank_stmt['date'].dt.strftime('%Y-%m-%d') + '|' +
            bank_stmt['amount_rounded'].astype(str) + '|' +
            bank_stmt['description'].str[:20].str.upper().str.strip()
        )

        # Find matches
        matched_gl = gl_cash[gl_cash['match_key'].isin(bank_stmt['match_key'])].copy()
        matched_bank = bank_stmt[bank_stmt['match_key'].isin(gl_cash['match_key'])].copy()

        # Identify unmatched transactions
        unmatched_gl = gl_cash[~gl_cash['match_key'].isin(bank_stmt['match_key'])].copy()
        unmatched_bank = bank_stmt[~bank_stmt['match_key'].isin(gl_cash['match_key'])].copy()

        print(f"\nReconciliation Results:")
        print(f"  Matched Transactions: {len(matched_gl)}")
        print(f"  Unmatched GL Transactions: {len(unmatched_gl)}")
        print(f"  Unmatched Bank Transactions: {len(unmatched_bank)}")

        # Calculate balances
        gl_balance = gl_cash['amount'].sum()
        bank_balance = bank_stmt['amount'].sum()
        matched_amount = matched_gl['amount'].sum() if len(matched_gl) > 0 else 0

        print(f"\nBalances:")
        print(f"  GL Cash Account Balance: {gl_balance:,.2f}")
        print(f"  Bank Statement Balance: {bank_balance:,.2f}")
        print(f"  Matched Amount: {matched_amount:,.2f}")
        print(f"  Difference: {bank_balance - gl_balance:,.2f}")

        # Prepare detailed results
        reconciliation_result = {
            'summary': {
                'gl_transactions': len(gl_cash),
                'bank_transactions': len(bank_stmt),
                'matched_transactions': len(matched_gl),
                'unmatched_gl': len(unmatched_gl),
                'unmatched_bank': len(unmatched_bank),
                'gl_balance': gl_balance,
                'bank_balance': bank_balance,
                'difference': bank_balance - gl_balance
            },
            'matched_transactions': pd.concat([matched_gl, matched_bank], ignore_index=True),
            'unmatched_gl': unmatched_gl[['date', 'description', 'amount', 'transaction_id']].copy(),
            'unmatched_bank': unmatched_bank[['date', 'description', 'amount']].copy() if 'transaction_id' not in bank_stmt.columns else unmatched_bank[['date', 'description', 'amount']].copy()
        }

        return reconciliation_result

    def intercompany_reconciliation(self, company_data_dict):
        """
        Perform intercompany reconciliation between multiple entities
        """
        print("=== Intercompany Reconciliation Process ===")

        # This would typically involve matching payables/receivables between entities
        # For demonstration, we'll create a simplified version

        results = {}

        # Assume we have data for multiple companies
        companies = list(company_data_dict.keys())
        if len(companies) < 2:
            print("ERROR: Need at least 2 companies for intercompany reconciliation")
            return None

        # Compare each pair of companies
        for i in range(len(companies)):
            for j in range(i+1, len(companies)):
                company_a = companies[i]
                company_b = companies[j]

                print(f"\nReconciling {company_a} vs {company_b}")

                # Get intercompany transactions (simplified)
                # In reality, these would be flagged intercompany accounts
                trans_a = company_data_dict[company_a].copy()
                trans_b = company_data_dict[company_b].copy()

                # For demo, we'll look for matching amounts with opposite signs
                # This is a simplified approach - real IC reconciliation is more complex

                matches = []  # Would contain matched pairs
                unmatched_a = trans_a  # Simplified
                unmatched_b = trans_b  # Simplified

                results[f"{company_a}_vs_{company_b}"] = {
                    'matches': matches,
                    'unmatched_a': unmatched_a,
                    'unmatched_b': unmatched_b
                }

                print(f"  Matches found: {len(matches)}")
                print(f"  Unmatched {company_a}: {len(unmatched_a)}")
                print(f"  Unmatched {company_b}: {len(unmatched_b)}")

        return results

    def trial_balance_reconciliation(self, trial_balance_period):
        """
        Verify that the trial balance balances (debits = credits)
        """
        print("=== Trial Balance Reconciliation ===")

        if 'financial_transactions' not in self.data:
            self.load_financial_data()

        # Get trial balance data (simplified - in practice this would come from a TB table)
        transactions = self.data['financial_transactions'].copy()

        # Filter to period if specified
        if trial_balance_period:
            # Assuming format like "2024-03" for year-month
            year, month = map(int, trial_balance_period.split('-'))
            tb_data = transactions[
                (transactions['transaction_date'].dt.year == year) &
                (transactions['transaction_date'].dt.month == month)
            ].copy()
        else:
            tb_data = transactions.copy()

        # Join with chart of accounts to get account types
        if 'chart_of_accounts' in self.data:
            tb_data = tb_data.merge(
                self.data['chart_of_accounts'][['account_id', 'account_type', 'account_category']],
                on='account_id',
                how='left'
            )

        # Calculate debits and credits by account type
        # Assuming: Debits increase assets/expenses, Credits increase liabilities/equity/revenue
        tb_data['debit_amount'] = 0
        tb_data['credit_amount'] = 0

        # Debits: Assets and Expenses increase with debits
        debit_accounts = ['Asset', 'Expense']
        tb_data.loc[tb_data['account_category'].isin(debit_accounts), 'debit_amount'] = tb_data['amount']

        # Credits: Liabilities, Equity, Revenue increase with credits
        credit_accounts = ['Liability', 'Equity', 'Revenue']
        tb_data.loc[tb_data['account_category'].isin(credit_accounts), 'credit_amount'] = tb_data['amount']

        # For negative amounts, reverse the logic
        tb_data.loc[tb_data['amount'] < 0, 'debit_amount'] = -tb_data['amount'] * (
            tb_data['account_category'].isin(credit_accounts)
        )
        tb_data.loc[tb_data['amount'] < 0, 'credit_amount'] = -tb_data['amount'] * (
            tb_data['account_category'].isin(debit_accounts)
        )

        # Calculate totals
        total_debits = tb_data['debit_amount'].sum()
        total_credits = tb_data['credit_amount'].sum()
        difference = total_debits - total_credits

        print(f"Period: {trial_balance_period or 'All Periods'}")
        print(f"Total Debits: {total_debits:,.2f}")
        print(f"Total Credits: {total_credits:,.2f}")
        print(f"Difference: {difference:,.2f}")

        if abs(difference) < 0.01:  # Essentially zero
            print("✓ TRIAL BALANCE IS IN BALANCE")
            balanced = True
        else:
            print("✗ TRIAL BALANCE IS OUT OF BALANCE")
            balanced = False

        # Show imbalance by account type if significant
        if abs(difference) > 1.00:
            imbalance_by_type = tb_data.groupby('account_category').agg({
                'debit_amount': 'sum',
                'credit_amount': 'sum'
            }).reset_index()
            imbalance_by_type['net'] = imbalance_by_type['debit_amount'] - imbalance_by_type['credit_amount']
            print("\nImbalance by Account Type:")
            for _, row in imbalance_by_type.iterrows():
                if abs(row['net']) > 0.01:
                    print(f"  {row['account_category']}: {row['net']:,.2f}")

        return {
            'balanced': balanced,
            'total_debits': total_debits,
            'total_credits': total_credits,
            'difference': difference,
            'transaction_count': len(tb_data)
        }

    def generate_reconciliation_report(self, reconciliation_results, output_file=None):
        """
        Generate a formatted reconciliation report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"reconciliation_report_{timestamp}.txt"

        with open(output_file, 'w') as f:
            f.write("FINANCIAL RECONCILIATION REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if isinstance(reconciliation_results, dict) and 'summary' in reconciliation_results:
                # Bank reconciliation format
                summary = reconciliation_results['summary']
                f.write("BANK RECONCILIATION SUMMARY\n")
                f.write("-" * 30 + "\n")
                f.write(f"GL Transactions: {summary['gl_transactions']:,}\n")
                f.write(f"Bank Transactions: {summary['bank_transactions']:,}\n")
                f.write(f"Matched Transactions: {summary['matched_transactions']:,}\n")
                f.write(f"Unmatched GL Transactions: {summary['unmatched_gl']:,}\n")
                f.write(f"Unmatched Bank Transactions: {summary['unmatched_bank']:,}\n")
                f.write(f"\nGL Balance: ${summary['gl_balance']:,.2f}\n")
                f.write(f"Bank Balance: ${summary['bank_balance']:,.2f}\n")
                f.write(f"Difference: ${summary['difference']:,.2f}\n\n")

                if summary['difference'] != 0:
                    f.write("RECONCILIATION ITEMS NEEDED:\n")
                    f.write("-" * 30 + "\n")
                    if len(reconciliation_results['unmatched_gl']) > 0:
                        f.write(f"Unmatched GL Items ({len(reconciliation_results['unmatched_gl'])}):\n")
                        for _, item in reconciliation_results['unmatched_gl'].head(10).iterrows():
                            f.write(f"  {item['date'].strftime('%Y-%m-%d')} | {item['description'][:30]:<30} | ${item['amount']:>10,.2f}\n")
                    if len(reconciliation_results['unmatched_bank']) > 0:
                        f.write(f"Unmatched Bank Items ({len(reconciliation_results['unmatched_bank'])}):\n")
                        for _, item in reconciliation_results['unmatched_bank'].head(10).iterrows():
                            f.write(f"  {item['date'].strftime('%Y-%m-%d')} | {item['description'][:30]:<30} | ${item['amount']:>10,.2f}\n")
            else:
                # Generic format
                f.write(str(reconciliation_results))

        print(f"Reconciliation report saved to: {output_file}")
        return output_file

def main():
    """
    Main function to demonstrate reconciliation functionality
    """
    print("Financial Reconciliation Demo")
    print("=" * 30)

    # Initialize reconciliation module
    reconciler = FinancialReconciliation()

    # Load financial data
    print("\nLoading financial data...")
    reconciler.load_financial_data()

    # Demonstrate trial balance reconciliation
    print("\n1. Trial Balance Reconciliation:")
    tb_result = reconciler.trial_balance_reconciliation(None)  # All periods

    # For bank reconciliation demo, we'd need a bank statement file
    # Let's create a sample bank statement for demonstration
    print("\n2. Creating sample bank statement for demo...")

    if 'financial_transactions' in reconciler.data:
        # Use some GL transactions as basis for bank statement
        gl_cash = reconciler.data['financial_transactions'][
            reconciler.data['financial_transactions']['account_id'] == '1000'
        ].copy()

        if len(gl_cash) > 0:
            # Create a sample bank statement with some variations
            bank_stmt = gl_cash[['transaction_date', 'description', 'amount']].copy()
            bank_stmt = bank_stmt.rename(columns={
                'transaction_date': 'date',
                'description': 'description',
                'amount': 'amount'
            })

            # Add some timing differences and errors for demo
            # Shift some dates by a few days
            if len(bank_stmt) > 2:
                # Modify a couple of dates to simulate timing differences
                idx_to_modify = min(2, len(bank_stmt)-1)
                bank_stmt.iloc[idx_to_modify, 0] = bank_stmt.iloc[idx_to_modify, 0] + timedelta(days=3)

                # Add a bank fee not in GL
                fee_row = pd.DataFrame({
                    'date': [bank_stmt['date'].min() + timedelta(days=5)],
                    'description': ['BANK SERVICE FEE'],
                    'amount': [-25.00]
                })
                bank_stmt = pd.concat([bank_stmt, fee_row], ignore_index=True)

                # Modify an amount to simulate bank error
                if len(bank_stmt) > 1:
                    idx_to_modify_amt = min(1, len(bank_stmt)-1)
                    original_amt = bank_stmt.iloc[idx_to_modify_amt]['amount']
                    bank_stmt.iloc[idx_to_modify_amt, 2] = original_amt * 1.02  # 2% error

            print(f"Created sample bank statement with {len(bank_stmt)} transactions")

            # Perform bank reconciliation
            print("\n3. Performing Bank Reconciliation:")
            bank_rec_result = reconciler.bank_reconciliation(bank_stmt, '1000')

            if bank_rec_result:
                # Generate report
                report_file = reconciler.generate_reconciliation_report(bank_rec_result)
                print(f"\nReconciliation complete. Report saved to: {report_file}")

    print("\nDemo completed!")

if __name__ == "__main__":
    main()
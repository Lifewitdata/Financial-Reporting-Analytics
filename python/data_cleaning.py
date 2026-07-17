#!/usr/bin/env python3
"""
Data Cleaning Module for Financial Data
This module provides functions to clean and preprocess financial data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDataCleaner:
    def __init__(self, data_dir='data'):
        """
        Initialize the data cleaner
        """
        self.data_dir = data_dir
        self.data = {}

    def load_csv(self, filename):
        """
        Load a CSV file and store it in the data dictionary
        """
        filepath = os.path.join(self.data_dir, filename)
        try:
            df = pd.read_csv(filepath)
            # Convert date columns if they exist
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            for col in date_columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

            self.data[filename.split('.')[0]] = df
            logger.info(f"Loaded {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return None

    def load_all_data(self):
        """
        Load all CSV files in the data directory
        """
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        for file in csv_files:
            self.load_csv(file)
        return self.data

    def clean_transactions_data(self, df=None):
        """
        Clean financial transactions data
        """
        if df is None:
            if 'financial_transactions' not in self.data:
                self.load_csv('financial_transactions.csv')
            df = self.data['financial_transactions'].copy()

        original_rows = len(df)

        # Remove duplicates
        df = df.drop_duplicates()

        # Handle missing values
        # For amount, fill with 0 or drop depending on business rules
        if 'amount' in df.columns:
            # Log missing amounts
            missing_amounts = df['amount'].isna().sum()
            if missing_amounts > 0:
                logger.warning(f"Found {missing_accounts} missing amounts - filling with 0")
                df['amount'] = df['amount'].fillna(0)

        # Validate account IDs exist in chart of accounts
        if 'chart_of_accounts' in self.data and 'account_id' in df.columns:
            valid_accounts = set(self.data['chart_of_accounts']['account_id'])
            invalid_accounts = df[~df['account_id'].isin(valid_accounts)]['account_id'].unique()
            if len(invalid_accounts) > 0:
                logger.warning(f"Found {len(invalid_accounts)} invalid account IDs: {list(invalid_accounts)[:5]}")
                # Optionally remove or flag these rows

        # Validate date ranges
        if 'transaction_date' in df.columns:
            # Check for future dates (beyond reasonable range)
            future_date = datetime.now().replace(year=datetime.now().year + 2)
            future_dates = df[df['transaction_date'] > future_date]
            if len(future_dates) > 0:
                logger.warning(f"Found {len(future_dates)} transactions with future dates")

            # Check for very old dates (before 2000)
            ancient_date = datetime(2000, 1, 1)
            old_dates = df[df['transaction_date'] < ancient_date]
            if len(old_dates) > 0:
                logger.warning(f"Found {len(old_dates)} transactions with dates before 2000")

        # Ensure amount is numeric
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            # Fill NaN amounts with 0
            df['amount'] = df['amount'].fillna(0)

        cleaned_rows = len(df)
        logger.info(f"Cleaned transactions data: {original_rows} → {cleaned_rows} rows "
                   f"(-{original_rows - cleaned_rows} duplicates/invalid)")

        self.data['financial_transactions_clean'] = df
        return df

    def clean_chart_of_accounts(self, df=None):
        """
        Clean chart of accounts data
        """
        if df is None:
            if 'chart_of_accounts' not in self.data:
                self.load_csv('chart_of_accounts.csv')
            df = self.data['chart_of_accounts'].copy()

        original_rows = len(df)

        # Remove duplicates
        df = df.drop_duplicates(subset=['account_id'])

        # Ensure account_id is string and trimmed
        if 'account_id' in df.columns:
            df['account_id'] = df['account_id'].astype(str).str.strip()

        # Ensure account_name is not null
        if 'account_name' in df.columns:
            null_names = df['account_name'].isna().sum()
            if null_names > 0:
                logger.warning(f"Found {null_names} accounts with missing names")
                # Fill with placeholder or drop
                df['account_name'] = df['account_name'].fillna('Unknown Account')

        # Standardize account categories
        if 'account_category' in df.columns:
            valid_categories = ['Asset', 'Liability', 'Equity', 'Revenue', 'Revenue', 'Expense']
            # You would typically map variations to standard categories here
            # For now, just log unexpected values
            invalid_cats = df[~df['account_category'].isin(valid_categories)]['account_category'].unique()
            if len(invalid_cats) > 0:
                logger.warning(f"Found unexpected account categories: {list(invalid_cats)}")

        cleaned_rows = len(df)
        logger.info(f"Cleaned chart of accounts: {original_rows} → {cleaned_rows} rows "
                   f"(-{original_rows - cleaned_rows} duplicates)")

        self.data['chart_of_accounts_clean'] = df
        return df

    def validate_fiscal_periods(self, df=None):
        """
        Validate that fiscal periods align with transaction dates
        """
        if df is None:
            if 'financial_transactions' not in self.data:
                self.load_csv('financial_transactions.csv')
            df = self.data['financial_transactions'].copy()

        if 'fiscal_calendar' not in self.data:
            self.load_csv('fiscal_calendar.csv')

        fiscal_cal = self.data['fiscal_calendar']

        # Merge to verify period dates match
        merged = df.merge(
            fiscal_cal,
            on=['fiscal_year', 'fiscal_period'],
            how='left',
            suffixes=('', '_cal')
        )

        # Check for mismatches
        date_mismatch = merged[
            (merged['transaction_date'] < merged['period_start_date']) |
            (merged['transaction_date'] > merged['period_end_date'])
        ]

        if len(date_mismatch) > 0:
            logger.warning(f"Found {len(date_mismatch)} transactions with dates outside their fiscal period")
            # Show first few mismatches
            for idx, row in date_mismatch.head().iterrows():
                logger.warning(f"  Transaction {row['transaction_id']}: "
                             f"Date {row['transaction_date']} not in period {row['fiscal_year']}-{row['fiscal_period']} "
                             f"({row['period_start_date']} to {row['period_end_date']})")

        return date_mismatch

    def generate_data_quality_report(self):
        """
        Generate a comprehensive data quality report
        """
        report = {}

        for key, df in self.data.items():
            if isinstance(df, pd.DataFrame):
                report[key] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'missing_values': df.isnull().sum().sum(),
                    'duplicate_rows': df.duplicated().sum(),
                    'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
                }

                # Column-specific info
                report[key]['columns_info'] = {}
                for col in df.columns:
                    col_info = {
                        'dtype': str(df[col].dtype),
                        'missing_count': df[col].isnull().sum(),
                        'unique_values': df[col].nunique()
                    }
                    if df[col].dtype in ['int64', 'float64']:
                        col_info.update({
                            'min': df[col].min(),
                            'max': df[col].max(),
                            'mean': df[col].mean(),
                            'std': df[col].std()
                        })
                    report[key]['columns_info'][col] = col_info

        return report

    def save_cleaned_data(self, output_dir='data/cleaned'):
        """
        Save cleaned data to CSV files
        """
        os.makedirs(output_dir, exist_ok=True)

        for key, df in self.data.items():
            if isinstance(df, pd.DataFrame) and '_clean' in key:
                filename = key.replace('_clean', '') + '_cleaned.csv'
                filepath = os.path.join(output_dir, filename)
                df.to_csv(filepath, index=False)
                logger.info(f"Saved cleaned data to {filepath}")

def main():
    """
    Main function to demonstrate data cleaning functionality
    """
    print("Financial Data Cleaning Demo")
    print("=" * 30)

    # Initialize cleaner
    cleaner = FinancialDataCleaner()

    # Load all data
    print("\nLoading data...")
    cleaner.load_all_data()

    # Generate initial data quality report
    print("\nGenerating initial data quality report...")
    initial_report = cleaner.generate_data_quality_report()

    for dataset, info in initial_report.items():
        print(f"\n{dataset.upper()}:")
        print(f"  Rows: {info['rows']:,}")
        print(f"  Columns: {info['columns']}")
        print(f"  Missing values: {info['missing_values']:,}")
        print(f"  Duplicate rows: {info['duplicate_rows']:,}")

    # Clean specific datasets
    print("\nCleaning financial transactions...")
    cleaner.clean_transactions_data()

    print("\nCleaning chart of accounts...")
    cleaner.clean_chart_of_accounts()

    # Validate fiscal periods
    print("\nValidating fiscal periods...")
    mismatches = cleaner.validate_fiscal_periods()
    if len(mismatches) > 0:
        print(f"Found {len(mismatches)} fiscal period mismatches")
    else:
        print("No fiscal period mismatches found")

    # Generate final data quality report
    print("\nGenerating final data quality report...")
    final_report = cleaner.generate_data_quality_report()

    for dataset, info in final_report.items():
        if '_clean' in dataset:
            print(f"\n{dataset.upper()}:")
            print(f"  Rows: {info['rows']:,}")
            print(f"  Columns: {info['columns']}")
            print(f"  Missing values: {info['missing_values']:,}")
            print(f"  Duplicate rows: {info['duplicate_rows']:,}")

    # Save cleaned data
    print("\nSaving cleaned data...")
    cleaner.save_cleaned_data()

    print("\nData cleaning complete!")

if __name__ == "__main__":
    main()
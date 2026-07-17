# Financial Reporting and Analytics - API Reference

## Core Classes

### FinancialAnalyzer
Main class for financial statement generation and analysis.

#### Constructor
```python
FinancialAnalyzer(data_dir='data')
```
- `data_dir`: Path to directory containing CSV data files

#### Methods

##### load_data()
Loads all required CSV files into memory.
```python
analyzer.load_data()
```

##### get_account_balance(account_id, start_date=None, end_date=None)
Calculates balance for a specific account.
- `account_id`: Account identifier (string)
- `start_date`: Start date for calculation (datetime, optional)
- `end_date`: End date for calculation (datetime, optional)
- Returns: Account balance as float

##### get_income_statement(fiscal_year, fiscal_period=None)
Generates income statement for specified period.
- `fiscal_year`: Fiscal year (integer)
- `fiscal_period`: Fiscal period (integer, optional - if None, returns full year)
- Returns: Dictionary with income statement components

##### get_balance_sheet(fiscal_year, fiscal_period=None)
Generates balance sheet for specified period.
- `fiscal_year`: Fiscal year (integer)
- `fiscal_period`: Fiscal period (integer, optional - if None, returns full year)
- Returns: Dictionary with balance sheet components

##### generate_financial_report(fiscal_year, fiscal_period=None)
Prints formatted income statement and balance sheet.
- `fiscal_year`: Fiscal year (integer)
- `fiscal_period`: Fiscal period (integer, optional)
- Returns: None (prints to console)

##### plot_monthly_revenue_trend(fiscal_year)
Creates and saves monthly revenue trend chart.
- `fiscal_year`: Fiscal year (integer)
- Saves: `revenue_trend_fy{year}.png`
- Displays: Interactive matplotlib chart

##### plot_expense_by_category(fiscal_year, fiscal_period=None)
Creates and saves expense by category chart.
- `fiscal_year`: Fiscal year (integer)
- `fiscal_period`: Fiscal period (integer, optional)
- Saves: `expenses_by_category_FY{year}_Period{period}.png`
- Displays: Interactive matplotlib chart

---

### KPIReporter
Class for calculating and reporting key performance indicators.

#### Constructor
```python
KPIReporter(data_dir='data')
```
- `data_dir`: Path to directory containing CSV data files

#### Methods

##### calculate_profitability_kpis(fiscal_year=None, fiscal_period=None)
Calculates profitability ratios.
- `fiscal_year`: Fiscal year (integer, optional)
- `fiscal_period`: Fiscal period (integer, optional)
- Returns: Dictionary with profitability KPIs

##### calculate_efficiency_kpis(fiscal_year=None, fiscal_period=None)
Calculates efficiency ratios.
- `fiscal_year`: Fiscal year (integer, optional)
- `fiscal_period`: Fiscal period (integer, optional)
- Returns: Dictionary with efficiency KPIs

##### calculate_liquidity_kpis()
Calculates liquidity ratios (based on YTD balances).
- Returns: Dictionary with liquidity KPIs

##### calculate_activity_kpis(fiscal_year=None)
Calculates activity/turnover ratios.
- `fiscal_year`: Fiscal year (integer, optional)
- Returns: Dictionary with activity KPIs

##### generate_kpi_report(fiscal_year=None, fiscal_period=None, output_dir='outputs')
Generates comprehensive KPI report.
- `fiscal_year`: Fiscal year (integer, optional)
- `fiscal_period`: Fiscal period (integer, optional)
- `output_dir`: Directory to save report (string, default: 'outputs')
- Returns: Path to generated report file

---

### FinancialReconciliation
Class for performing various financial reconciliations.

#### Constructor
```python
FinancialReconciliation(data_dir='data')
```
- `data_dir`: Path to directory containing CSV data files

#### Methods

##### load_data(filename)
Loads a specific CSV file.
- `filename`: Name of CSV file to load (string)
- Returns: Pandas DataFrame

##### load_financial_data()
Loads essential financial data for reconciliation.
- Returns: None (loads data into internal dictionary)

##### bank_reconciliation(bank_statement_df, gl_account_cash='1000')
Performs bank reconciliation between GL and bank statement.
- `bank_statement_df`: Pandas DataFrame containing bank statement data
- `gl_account_cash`: GL account ID for cash account (string, default: '1000')
- Returns: Dictionary with reconciliation results

##### intercompany_reconciliation(company_data_dict)
Performs intercompany reconciliation between entities.
- `company_data_dict`: Dictionary mapping company names to transaction DataFrames
- Returns: Dictionary with reconciliation results for each company pair

##### trial_balance_reconciliation(trial_balance_period=None)
Verifies that debits equal credits.
- `trial_balance_period`: Period to check in "YYYY-MM" format (string, optional)
- Returns: Dictionary with reconciliation results

##### generate_reconciliation_report(reconciliation_results, output_file=None)
Generates formatted reconciliation report.
- `reconciliation_results`: Dictionary from reconciliation methods
- `output_file`: Path to save report (string, optional)
- Returns: Path to generated report file

---

### DataCleaner
Class for cleaning and preprocessing financial data.

#### Constructor
```python
FinancialDataCleaner(data_dir='data')
```
- `data_dir`: Path to directory containing CSV data files

#### Methods

##### load_csv(filename)
Loads a specific CSV file.
- `filename`: Name of CSV file to load (string)
- Returns: Pandas DataFrame

##### load_all_data()
Loads all CSV files in the data directory.
- Returns: Dictionary mapping filenames to DataFrames

##### clean_transactions_data(df=None)
Cleans financial transactions data.
- `df`: Pandas DataFrame to clean (optional - if None, loads from internal data)
- Returns: Cleaned Pandas DataFrame

##### clean_chart_of_accounts(df=None)
Cleans chart of accounts data.
- `df`: Pandas DataFrame to clean (optional - if None, loads from internal data)
- Returns: Cleaned Pandas DataFrame

##### validate_fiscal_periods(df=None)
Validates that transaction dates align with fiscal periods.
- `df`: Pandas DataFrame to validate (optional - if None, uses transactions data)
- Returns: DataFrame of mismatched transactions

##### generate_data_quality_report()
Generates comprehensive data quality report.
- Returns: Dictionary with data quality metrics for each dataset

##### save_cleaned_data(output_dir='data/cleaned')
Saves cleaned data to CSV files.
- `output_dir`: Directory to save cleaned data (string, default: 'data/cleaned')
- Returns: None

---

## Utility Methods)

All classes include these utility methods:

#### __str__()
Returns string representation of the object.

#### __repr__()
Returns detailed string representation for debugging.

## Data Models

### Financial Transaction Schema
- `transaction_id`: Unique identifier (string)
- `transaction_date`: Date of transaction (date)
- `fiscal_year`: Fiscal year (integer)
- `fiscal_period`: Fiscal period (integer)
- `account_id`: Account identifier (string, foreign key to chart_of_accounts)
- `department_id`: Department identifier (string, foreign key to departments)
- `amount`: Transaction amount (decimal)
- `description`: Transaction description (text)
- `currency`: Currency code (string, default: 'USD')

### Chart of Accounts Schema
- `account_id`: Unique account identifier (string, primary key)
- `account_name`: Account name (string)
- `account_type`: Account type (string: Asset, Liability, Equity, Revenue, Expense)
- `account_category`: Account category (string: Current Asset, Fixed Asset, Current Liability, etc.)
- `is_active`: Whether account is active (boolean)

### Department Schema
- `department_id`: Unique department identifier (string, primary key)
- `department_name`: Department name (string)
- `department_head`: Department head name (string)
- `cost_center`: Cost center code (string)

### Fiscal Calendar Schema
- `fiscal_year`: Fiscal year (integer, part of primary key)
- `fiscal_period`: Fiscal period (integer, part of primary key)
- `period_start_date`: Start date of period (date)
- `period_end_date`: End date of period (date)
- `quarter`: Quarter designation (string: Q1, Q2, Q3, Q4)

## Error Handling

All methods raise appropriate exceptions for error conditions:

### FileNotFoundError
Raised when required data files are missing from the data directory.

### ValueError
Raised when invalid parameters are passed to methods.

### KeyError
Raised when referencing non-existent accounts, departments, or fiscal periods.

### RuntimeError
Raised when operations cannot be completed due to data inconsistencies.

## Usage Examples

### Basic Financial Analysis
```python
from financial_analyzer import FinancialAnalyzer

# Initialize analyzer
analyzer = FinancialAnalyzer()

# Load data
analyzer.load_data()

# Generate reports
analyzer.generate_financial_report(2024, 1)  # Q1 2024
analyzer.generate_financial_report(2024)     # Full year 2024

# Create visualizations
analyzer.plot_monthly_revenue_trend(2024)
analyzer.plot_expense_by_category(2024, 1)
```

### KPI Reporting
```python
from kpi_report import KPIReporter

# Initialize KPI reporter
reporter = KPIReporter()

# Generate KPI report
report_path = reporter.generate_kpi_report(2024, 1)
print(f"KPI report saved to: {report_path}")

# Get specific KPI sets
profitability = reporter.calculate_profitability_kpis(2024, 1)
liquidity = reporter.calculate_liquidity_kpis()
```

### Reconciliation
```python
from reconciliation import FinancialReconciliation
import pandas as pd

# Initialize reconciler
reconciler = FinancialReconciliation()
reconciler.load_financial_data()

# Load bank statement (example)
bank_stmt = pd.read_csv('bank_statement_jan2024.csv')
bank_stmt['date'] = pd.to_datetime(bank_stmt['date'])

# Perform bank reconciliation
result = reconciler.bank_reconciliation(bank_stmt, '1000')

# Generate report
report_file = reconciler.generate_reconciliation_report(result)
print(f"Reconciliation report saved to: {report_file}")
```

## Extending the System

### Adding New Reports
1. Create a new Python class inheriting from existing base classes
2. Override or extend methods as needed
3. Add new visualization or calculation methods
4. Update the main financial_analyzer.py to use the new class

### Custom KPIs
1. Add new methods to KPIReporter class
2. Implement the calculation logic
3. Update generate_kpi_report() to include new KPIs
4. Add appropriate formatting to the report output

### Database Integration
1. Replace CSV loading methods with database queries
2. Update schema.sql with your actual database schema
3. Modify load_data() methods to use database connections
4. Keep the same method signatures for compatibility

## Version Information
- **Version**: 1.0.0
- **Python Compatibility**: 3.8+
- **Last Updated**: 2024-01-17
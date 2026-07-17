# Financial Reporting Analytics Notebooks

This directory contains Jupyter notebooks for exploratory financial data analysis.

## Available Notebooks

- `01_data_exploration.ipynb` - Initial data exploration and profiling
- `02_financial_statement_analysis.ipynb` - Income statement, balance sheet, and cash flow analysis
- `03_kpi_dashboard.ipynb` - Key performance indicator tracking and visualization
- `04_budget_variance_analysis.ipynb` - Budget vs actual variance analysis
- `05_consolidated_reporting.ipynb` - Multi-entity consolidation and reporting

## Usage

To run the notebooks:
1. Install required packages: `pip install -r requirements.txt`
2. Launch Jupyter: `jupyter notebook`
3. Open the desired notebook from this directory

## Data Sources

Notebooks use data from the `data/` directory:
- `financial_transactions.csv` - General ledger transactions
- `chart_of_accounts.csv` - Account master data
- `departments.csv` - Organizational structure
- `fiscal_calendar.csv` - Fiscal period definitions

## Example Analysis

Typical notebook analyses include:
- Trend analysis of revenues and expenses
- Department-level profitability analysis
- Cash flow forecasting
- Variance analysis against budgets
- Financial ratio calculations and benchmarking
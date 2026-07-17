# Financial Reporting and Analytics - Quick Start Guide

## 5-Minute Setup Guide

Follow these steps to get the financial reporting system up and running quickly.

### Step 1: Environment Setup
```bash
# Clone the repository (if not already done)
git clone [repository-url]
cd Financial-Reporting-Analytics

# Create and activate virtual environment (recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On MacOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Verify Installation
Check that the sample data files exist:
```bash
ls data/
# Should see: chart_of_accounts.csv, departments.csv, financial_transactions.csv, fiscal_calendar.csv
```

### Step 4: Run Your First Analysis
```bash
python financial_analyzer.py
```

You should see output similar to:
```
Financial Reporting and Analytics Demo
======================================

Loading data...
Loaded financial_transactions: 30 rows, 9 columns
Loaded chart_of_accounts: 30 rows, 5 columns
Loaded departments: 8 rows, 4 columns
Loaded fiscal_calendar: 15 rows, 5 columns

Generating Q1 2024 Financial Report...
...

Demo completed!
```

### Step 5: Check Outputs
Examine the generated files:
```bash
ls outputs/
# Should see generated charts and reports
```

## Common Tasks

### Generate a Financial Report
```python
from financial_analyzer import FinancialAnalyzer

analyzer = FinancialAnalyzer()
# Generate income statement and balance sheet for Q1 2024
analyzer.generate_financial_report(fiscal_year=2024, fiscal_period=1)
```

### Create a Revenue Trend Chart
```python
analyzer.plot_monthly_revenue_trend(fiscal_year=2024)
```

### Calculate KPIs
```python
from kpi_report import KPIReporter

reporter = KPIReporter()
kpis = reporter.generate_kpi_report(fiscal_year=2024)
print(kpis)
```

### Perform Bank Reconciliation
```python
from reconciliation import FinancialReconciliation

reconciler = FinancialReconciliation()
reconciler.load_financial_data()

# Assuming you have a bank statement DataFrame called 'bank_stmt'
result = reconciler.bank_reconciliation(bank_stmt, '1000')
```

## Next Steps

1. **Explore the Sample Data**: Look at the CSV files in the data/ directory to understand the data structure
2. **Customize for Your Data**: Replace sample files with your actual financial data
3. **Try the Notebooks**: Run the Jupyter notebooks in the notebooks/ directory for interactive exploration
4. **Read the User Guide**: Check documentation/user_guide.md for detailed instructions
5. **Build Custom Reports**: Extend the Python classes to create reports specific to your organization

## Need Help?

- Review the README.md for project overview
- Check individual Python file docstrings for function details
- Look at the SQL files for database implementation patterns
- Examine the sample data to understand expected formats

You're now ready to start analyzing financial data and generating reports!
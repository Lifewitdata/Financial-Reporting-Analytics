-- Financial Reporting Database Views
-- These views provide commonly used financial reporting perspectives

-- View: Account Balances by Period
-- Shows the running balance for each account up to each period
CREATE OR REPLACE VIEW v_account_balances AS
SELECT
    ft.account_id,
    coa.account_name,
    coa.account_type,
    coa.account_category,
    ft.fiscal_year,
    ft.fiscal_period,
    SUM(ft.amount) OVER (
        PARTITION BY ft.account_id
        ORDER BY ft.fiscal_year, ft.fiscal_period
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS period_balance,
    SUM(ft.amount) OVER (
        PARTITION BY ft.account_id
        ORDER BY ft.fiscal_year, ft.fiscal_period
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS year_to_date_balance
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
WHERE coa.is_active = TRUE
ORDER BY ft.account_id, ft.fiscal_year, ft.fiscal_period;

-- View: Department Expenses Summary
-- Shows total expenses by department and period
CREATE OR REPLACE VIEW v_department_expenses AS
SELECT
    d.department_id,
    d.department_name,
    d.cost_center,
    ft.fiscal_year,
    ft.fiscal_period,
    SUM(CASE WHEN coa.account_category = 'Expense' THEN ft.amount ELSE 0 END) AS total_expenses,
    SUM(CASE WHEN coa.account_category = 'Operating Expense' THEN ft.amount ELSE 0 END) AS operating_expenses,
    COUNT(ft.transaction_id) AS transaction_count
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
JOIN departments d ON ft.department_id = d.department_id
WHERE coa.is_active = TRUE
GROUP BY d.department_id, d.department_name, d.cost_center, ft.fiscal_year, ft.fiscal_period
ORDER BY d.department_name, ft.fiscal_year, ft.fiscal_period;

-- View: Revenue Summary
-- Shows revenue by type and period
CREATE OR REPLACE VIEW v_revenue_summary AS
SELECT
    ft.fiscal_year,
    ft.fiscal_period,
    coa.account_name,
    SUM(ft.amount) AS revenue_amount,
    COUNT(ft.transaction_id) AS transaction_count
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
WHERE coa.account_category = 'Operating Revenue'
    AND coa.is_active = TRUE
GROUP BY ft.fiscal_year, ft.fiscal_period, coa.account_name
ORDER BY ft.fiscal_year, ft.fiscal_period, coa.account_name;

-- View: Income Statement Components
-- Breaks down income statement components by period
CREATE OR REPLACE VIEW v_income_statement AS
SELECT
    ft.fiscal_year,
    ft.fiscal_period,
    -- Revenue Accounts
    SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END) AS total_revenue,
    -- Cost of Goods Sold
    SUM(CASE WHEN coa.account_category = 'COGS' THEN ft.amount ELSE 0 END) AS cogs,
    -- Operating Expenses by category
    SUM(CASE WHEN coa.account_category = 'Operating Expense' THEN ft.amount ELSE 0 END) AS operating_expenses,
    -- Non-operating items
    SUM(CASE WHEN coa.account_category = 'Non-Operating Revenue' THEN ft.amount ELSE 0 END) AS non_operating_revenue,
    SUM(CASE WHEN coa.account_category = 'Non-Operating Expense' THEN ft.amount ELSE 0 END) AS non_operating_expense,
    -- Calculated fields
    SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END) -
    SUM(CASE WHEN coa.account_category = 'COGS' THEN ft.amount ELSE 0 END) AS gross_profit,
    SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END) -
    SUM(CASE WHEN coa.account_category = 'COGS' THEN ft.amount ELSE 0 END) -
    SUM(CASE WHEN coa.account_category = 'Operating Expense' THEN ft.amount ELSE 0 END) AS operating_income
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
WHERE coa.is_active = TRUE
GROUP BY ft.fiscal_year, ft.fiscal_period
ORDER BY ft.fiscal_year, ft.fiscal_period;

-- View: Balance Sheet Components
-- Shows assets, liabilities, and equity balances
CREATE OR REPLACE VIEW v_balance_sheet AS
SELECT
    'Assets' AS statement_section,
    coa.account_category AS category,
    coa.account_name,
    SUM(ft.amount) AS balance
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
WHERE coa.account_category IN ('Asset')
    AND coa.is_active = TRUE
GROUP BY coa.account_category, coa.account_name

UNION ALL

SELECT
    'Liabilities' AS statement_section,
    coa.account_category AS category,
    coa.account_name,
    SUM(ft.amount) AS balance
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
WHERE coa.account_category IN ('Liability')
    AND coa.is_active = TRUE
GROUP BY coa.account_category, coa.account_name

UNION ALL

SELECT
    'Equity' AS statement_section,
    coa.account_category AS category,
    coa.account_name,
    SUM(ft.amount) AS balance
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
WHERE coa.account_category IN ('Equity')
    AND coa.is_active = TRUE
GROUP BY coa.account_category, coa.account_name

ORDER BY
    CASE statement_section
        WHEN 'Assets' THEN 1
        WHEN 'Liabilities' THEN 2
        WHEN 'Equity' THEN 3
    END,
    category,
    account_name;
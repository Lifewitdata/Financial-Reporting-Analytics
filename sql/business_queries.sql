-- Financial Reporting Business Queries
-- Common financial analysis queries for reporting and analysis

-- Query 1: Monthly Revenue Trend Analysis
-- Shows month-over-month revenue growth
SELECT
    fiscal_year,
    fiscal_period,
    SUM(amount) AS monthly_revenue,
    LAG(SUM(amount)) OVER (ORDER BY fiscal_year, fiscal_period) AS previous_month_revenue,
    CASE
        WHEN LAG(SUM(amount)) OVER (ORDER BY fiscal_year, fiscal_period) IS NULL OR
             LAG(SUM(amount)) OVER (ORDER BY fiscal_year, fiscal_period) = 0
        THEN NULL
        ELSE
            ROUND(
                (SUM(amount) - LAG(SUM(amount)) OVER (ORDER BY fiscal_year, fiscal_period)) * 100.0 /
                LAG(SUM(amount)) OVER (ORDER BY fiscal_year, fiscal_period), 2
            )
    END AS mom_growth_percent
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
WHERE coa.account_category = 'Operating Revenue'
    AND coa.is_active = TRUE
GROUP BY fiscal_year, fiscal_period
ORDER BY fiscal_year, fiscal_period;

-- Query 2: Expense Analysis by Department
-- Shows total expenses by department with percentage of total
SELECT
    d.department_name,
    SUM(CASE WHEN coa.account_category = 'Expense' THEN ft.amount ELSE 0 END) AS total_expenses,
    ROUND(
        SUM(CASE WHEN coa.account_category = 'Expense' THEN ft.amount ELSE 0 END) * 100.0 /
        SUM(SUM(CASE WHEN coa.account_category = 'Expense' THEN ft.amount ELSE 0 END)) OVER (), 2
    ) AS expense_percentage_of_total
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
JOIN departments d ON ft.department_id = d.department_id
WHERE coa.is_active = TRUE
GROUP BY d.department_name
ORDER BY total_expenses DESC;

-- Query 3: Budget vs Actual Analysis
-- Compares actual spending to budgeted amounts (requires budget table)
-- Note: This assumes a budget table exists with similar structure
SELECT
    d.department_name,
    coa.account_name,
    SUM(ft.amount) AS actual_amount,
    COALESCE(b.budget_amount, 0) AS budget_amount,
    SUM(ft.amount) - COALESCE(b.budget_amount, 0) AS variance,
    CASE
        WHEN COALESCE(b.budget_amount, 0) = 0
        THEN NULL
        ELSE ROUND(
            (SUM(ft.amount) - COALESCE(b.budget_amount, 0)) * 100.0 /
            COALESCE(b.budget_amount, 1), 2
        )
    END AS variance_percent
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
JOIN departments d ON ft.department_id = d.department_id
LEFT JOIN budget b ON
    ft.account_id = b.account_id AND
    ft.department_id = b.department_id AND
    ft.fiscal_year = b.fiscal_year AND
    ft.fiscal_period = b.fiscal_period
WHERE coa.is_active = TRUE
GROUP BY d.department_name, coa.account_name, b.budget_amount
ORDER BY variance DESC;

-- Query 4: Cash Flow Statement (Indirect Method)
-- Shows cash flow from operating activities
WITH net_income AS (
    SELECT
        fiscal_year,
        fiscal_period,
        SUM(CASE
            WHEN coa.account_category IN ('Operating Revenue', 'Non-Operating Revenue') THEN ft.amount
            WHEN coa.account_category IN ('Operating Expense', 'COGS', 'Non-Operating Expense') THEN -ft.amount
            ELSE 0
        END) AS net_income
    FROM financial_transactions ft
    JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
    WHERE coa.is_active = TRUE
    GROUP BY fiscal_year, fiscal_period
),
working_capital_changes AS (
    SELECT
        fiscal_year,
        fiscal_period,
        -- Changes in current assets (increase = use of cash)
        -SUM(CASE
            WHEN coa.account_category IN ('Current Asset') THEN ft.amount
            ELSE 0
        END) +
        -- Changes in current liabilities (increase = source of cash)
        SUM(CASE
            WHEN coa.account_category IN ('Current Liability') THEN ft.amount
            ELSE 0
        END) AS working_capital_change
    FROM financial_transactions ft
    JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
    WHERE coa.is_active = TRUE
        AND coa.account_category IN ('Current Asset', 'Current Liability')
    GROUP BY fiscal_year, fiscal_period
)
SELECT
    ni.fiscal_year,
    ni.fiscal_period,
    ni.net_income,
    COALESCE(wcc.working_capital_change, 0) AS working_capital_change,
    ni.net_income + COALESCE(wcc.working_capital_change, 0) AS cash_flow_from_operations
FROM net_income ni
LEFT JOIN working_capital_changes wcc ON
    ni.fiscal_year = wcc.fiscal_year AND
    ni.fiscal_period = wcc.fiscal_period
ORDER BY ni.fiscal_year, ni.fiscal_period;

-- Query 5: Top 10 Expenses by Amount
-- Identifies the largest expense transactions
SELECT
    ft.transaction_date,
    ft.transaction_id,
    d.department_name,
    coa.account_name,
    ft.amount,
    ft.description
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
JOIN departments d ON ft.department_id = d.department_id
WHERE coa.account_category = 'Expense'
    AND coa.is_active = TRUE
ORDER BY ft.amount DESC
LIMIT 10;

-- Query 6: Monthly Profitability Ratios
-- Calculates key profitability metrics
SELECT
    fiscal_year,
    fiscal_period,
    -- Gross Profit Margin
    CASE
        WHEN SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END) = 0
        THEN NULL
        ELSE ROUND(
            (SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END) -
             SUM(CASE WHEN coa.account_category = 'COGS' THEN ft.amount ELSE 0 END)) * 100.0 /
            SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END), 2
        )
    END AS gross_profit_margin_percent,
    -- Operating Margin
    CASE
        WHEN SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END) = 0
        THEN NULL
        ELSE ROUND(
            (SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END) -
             SUM(CASE WHEN coa.account_category = 'COGS' THEN ft.amount ELSE 0 END) -
             SUM(CASE WHEN coa.account_category = 'Operating Expense' THEN ft.amount ELSE 0 END)) * 100.0 /
            SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END), 2
        )
    END AS operating_margin_percent,
    -- Net Profit Margin
    CASE
        WHEN SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END) = 0
        THEN NULL
        ELSE ROUND(
            (SUM(CASE WHEN coa.account_category IN ('Operating Revenue', 'Non-Operating Revenue') THEN ft.amount ELSE 0 END) -
             SUM(CASE WHEN coa.account_category IN ('Operating Expense', 'COGS', 'Non-Operating Expense') THEN ft.amount ELSE 0 END)) * 100.0 /
            SUM(CASE WHEN coa.account_category = 'Operating Revenue' THEN ft.amount ELSE 0 END), 2
        )
    END AS net_profit_margin_percent
FROM financial_transactions ft
JOIN chart_of_accounts coa ON ft.account_id = coa.account_id
WHERE coa.is_active = TRUE
GROUP BY fiscal_year, fiscal_period
ORDER BY fiscal_year, fiscal_period;
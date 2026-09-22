# Smart Personal Finance Tracker 💰📊

A professional-grade, modular Personal Finance Tracker engineered with advanced Object-Oriented Programming (OOP) in Python, featuring SQLite database persistence, dynamic financial balance reconciliation, intelligent budget tracking with rollover support, automated statistical outlier detection, predictive spending forecasting, and an executive reporting engine.

---

## 🏛️ 1. Architecture & Design Principles

The application is structured strictly following **SOLID principles** and Clean Architecture:

* **Single Responsibility Principle (SRP):** Distinct modules encapsulate domain models (`Account`, `Transaction`, `Budget`), database access (`DatabaseManager`), analytics & forecasting (`FinancialAnalytics`), reporting (`ReportGenerator`), and presentation (`FinanceTrackerGUI` / CLI).
* **Open/Closed Principle (OCP):** New account types inherit from the abstract base class `Account` with polymorphic implementations without modifying existing business logic.
* **Liskov Substitution Principle (LSP):** Concrete accounts (`CheckingAccount`, `SavingsAccount`, `CashAccount`, `InvestmentAccount`) can be used interchangeably throughout the ledger and transfer workflows.
* **Interface Segregation & Encapsulation:** Account balances, transaction amounts, and limits are managed strictly via private/protected attributes and validated properties.
* **Financial Precision:** All monetary amounts use `decimal.Decimal` with 2-place half-up quantization, eliminating floating-point rounding bugs.

---

## 📁 2. Modular Project Structure

```
├── main.py               # Application entry point (CLI, GUI, Tests, Seeder, Reports)
├── finance_tracker.py    # Master domain orchestrator (FinanceTracker)
├── account.py            # Account domain hierarchy (Checking, Savings, Cash, Investment)
├── transaction.py        # Transaction model (Income, Expense, Transfer, Recurring)
├── budget.py             # Intelligent budget manager (Limits, 80% warnings, Rollover)
├── database.py           # SQLite operations with ACID transactions, indexing & backup
├── analytics.py          # Financial analytics, IQR & Z-score anomaly detector, forecasting
├── reports.py            # Financial statement generator (Text, HTML/PDF-ready, CSV)
├── validators.py         # Strict input validation & sanitization
├── exceptions.py         # Custom domain exception hierarchy
├── sample_data.py        # Realistic multi-month financial seed dataset
├── gui.py                # Desktop GUI implementation (Tkinter + Matplotlib)
├── requirements.txt      # Python dependencies
├── tests/                # Automated test suite (22+ unit and integration tests)
│   ├── __init__.py
│   ├── test_finance_tracker.py
│   ├── test_analytics.py
│   ├── test_budget.py
│   └── test_database.py
└── server.ts             # Full-stack API bridge & Web UI server for AI Studio
```

---

## 🚀 3. Installation & Quick Start

### Prerequisites
* Python 3.8 or higher.
* Standard library includes `sqlite3`, `decimal`, `statistics`, `unittest`.
* Optional GUI enhancements: `pip install -r requirements.txt`.

### Execution Modes

1. **Automated Test Suite (Unittest):**
   ```bash
   python3 main.py --test
   # Or directly:
   python3 -m unittest discover tests -v
   ```

2. **Generate Executive Financial Summary:**
   ```bash
   python3 main.py --report text
   ```

3. **Export Reports to HTML or CSV:**
   ```bash
   python3 main.py --report html > financial_statement.html
   python3 main.py --report csv > transactions.csv
   ```

4. **Seed Sample Data:**
   ```bash
   python3 main.py --seed
   ```

5. **Interactive Terminal CLI Mode:**
   ```bash
   python3 main.py --cli
   ```

6. **Launch Desktop Graphical Interface:**
   ```bash
   python3 main.py --gui
   ```

---

## 🔬 4. Analytics & Predictive Methodologies

* **Statistical Outlier Detection:** Combines **Interquartile Range (IQR)** with **Modified Z-Scores** based on Median Absolute Deviation (MAD), identifying transactions that significantly deviate from categorical norms without being skewed by extreme values.
* **Future Expense Forecasting:** Employs **Simple Exponential Smoothing ($\alpha = 0.5$)** over historical monthly expenses to project upcoming expenditure and net savings with empirical confidence bounds.
* **Recurring Subscriptions:** Identifies repeating expense amounts and regular cadence intervals (weekly, monthly, annual) across merchants.
* **Financial Health Score (0-100):** Transparent, multi-factor scorecard evaluating:
  * Savings Rate (30 pts)
  * Budget Discipline & Overrun Avoidance (30 pts)
  * Emergency Liquidity Buffer (25 pts)
  * Outlier Spending Volatility (15 pts)

---

## 🔒 5. Database Schema & Security

The SQLite database (`finance_tracker.db`) enforces:
* **Foreign Key Constraints:** `PRAGMA foreign_keys = ON;`
* **Performance Indexes:** Date, category, account_id, and budget period lookups.
* **Audit Trail:** Every account creation, transaction modification, deletion, and database restore is timestamped in the `audit_logs` table.
* **Safe Parameterized Queries:** Zero string interpolation in SQL commands protects against injection attacks.
* **Atomic Backup & Restore:** Built-in `backup_to_file()` and `restore_from_file()` methods with schema validation.

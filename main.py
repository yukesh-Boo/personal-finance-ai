"""Application entry point for Smart Personal Finance Tracker.

Supports GUI execution, interactive terminal CLI mode, automated tests,
sample data seeding, and standalone financial report generation.
"""

import argparse
import sys
import os
from decimal import Decimal

from finance_tracker import FinanceTracker
from sample_data import seed_sample_data


def run_interactive_cli(tracker: FinanceTracker) -> None:
    """Provides a terminal-driven interactive interface."""
    print("\n" + "=" * 60)
    print("      SMART PERSONAL FINANCE TRACKER - INTERACTIVE CLI")
    print("=" * 60)

    while True:
        print("\nCommands:")
        print("  1. View Financial Executive Summary")
        print("  2. List All Accounts & Balances")
        print("  3. View Recent Transactions")
        print("  4. Add Transaction (Income / Expense / Transfer)")
        print("  5. View Active Budgets & Overrun Alerts")
        print("  6. View Statistical Outliers & Anomaly Alerts")
        print("  7. View Subscriptions & Recurring Charges")
        print("  8. View Next-Month Spending Forecast")
        print("  9. Export Executive Report (Text / HTML / CSV)")
        print("  10. Re-seed Sample Financial Records")
        print("  0. Exit")

        choice = input("\nEnter choice [0-10]: ").strip()

        if choice == "0":
            print("Exiting Finance Tracker. Goodbye!")
            break
        elif choice == "1":
            print("\n" + tracker.generate_report("text"))
        elif choice == "2":
            accounts = tracker.get_all_accounts()
            print("\n--- ACCOUNTS ---")
            for a in accounts:
                print(f"[{a.account_type.value.upper():<10}] {a.name:<25} ${a.balance:,.2f} ({a.currency})")
        elif choice == "3":
            txns = tracker.get_transactions(limit=15)
            print("\n--- RECENT TRANSACTIONS ---")
            for t in txns:
                sign = "+" if t["type"] == "income" else ("-" if t["type"] == "expense" else "⇄")
                print(f"{t['date']} | {t['type']:<8} | {t['category']:<20} | {sign}${Decimal(t['amount']):,.2f} | {t.get('description', '')}")
        elif choice == "4":
            try:
                ttype = input("Type (income/expense/transfer): ").strip().lower()
                amt = input("Amount ($): ").strip()
                cat = input("Category (e.g. Groceries, Salary): ").strip()
                acc_name = input("Account Name (e.g. Chase Checking): ").strip()
                acc = tracker.get_account(acc_name)
                desc = input("Description: ").strip()

                target_id = None
                if ttype == "transfer":
                    target_name = input("Destination Account Name: ").strip()
                    target_acc = tracker.get_account(target_name)
                    target_id = target_acc.id

                tracker.add_transaction(
                    amount=amt,
                    transaction_type=ttype,
                    category=cat,
                    account_id=acc.id,
                    target_account_id=target_id,
                    description=desc,
                )
                print(">> Transaction successfully recorded!")
            except Exception as e:
                print(f"Error: {e}")
        elif choice == "5":
            budgets = tracker.evaluate_budgets()
            print("\n--- BUDGET EVALUATIONS ---")
            for b in budgets:
                print(f"{b['category']:<20} Spent: ${Decimal(b['actual_spent']):,.2f} / ${Decimal(b['effective_limit']):,.2f} ({b['utilization_percentage']:.1f}%) [{b['status']}]")
        elif choice == "6":
            dossier = tracker.get_analytics_dossier()
            outliers = dossier["anomalous_outliers"]
            print("\n--- STATISTICAL OUTLIER SPENDING ---")
            if not outliers:
                print("No anomalous transactions detected. Spending is stable.")
            else:
                for o in outliers:
                    print(f"Alert on {o['date']} | {o['category']} | ${o['amount']} (Z={o['z_score']}) -> {o['anomaly_reason']}")
        elif choice == "7":
            dossier = tracker.get_analytics_dossier()
            subs = dossier["subscriptions"]
            print("\n--- DETECTED RECURRING CHARGES ---")
            for s in subs:
                print(f"{s['name']:<25} ${s['typical_amount']} ({s['cadence']}) [Last: {s['last_billed']}]")
        elif choice == "8":
            dossier = tracker.get_analytics_dossier()
            fc = dossier["forecast"]
            print("\n--- NEXT MONTH FORECAST ---")
            if fc.get("has_sufficient_data"):
                print(f"Forecast Month:         {fc['forecast_month']}")
                print(f"Estimated Expenses:     ${fc['estimated_expenses']} (Range: ${fc['expenses_lower_bound']} - ${fc['expenses_upper_bound']})")
                print(f"Projected Income:       ${fc['projected_income']}")
                print(f"Estimated Net Savings:  ${fc['projected_net_savings']} ({fc['projected_savings_rate_pct']}%)")
                print(f"\n{fc['disclaimer']}")
            else:
                print(fc.get("disclaimer"))
        elif choice == "9":
            fmt = input("Format (text/html/csv): ").strip().lower()
            content = tracker.generate_report(fmt)
            filename = f"report_export.{fmt if fmt != 'text' else 'txt'}"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f">> Report saved to {filename}")
        elif choice == "10":
            seed_sample_data(tracker)
            print(">> Realistic financial history seeded successfully!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Smart Personal Finance Tracker")
    parser.add_argument("--gui", action="store_true", help="Launch Tkinter Graphical User Interface")
    parser.add_argument("--cli", action="store_true", help="Launch interactive Terminal Command-Line Interface")
    parser.add_argument("--seed", action="store_true", help="Seed realistic sample financial data into database")
    parser.add_argument("--report", choices=["text", "html", "csv"], help="Generate and print executive financial report")
    parser.add_argument("--db", default="finance_tracker.db", help="Path to SQLite database file")
    parser.add_argument("--test", action="store_true", help="Run automated test suite")

    args = parser.parse_args()

    if args.test:
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

    tracker = FinanceTracker(db_path=args.db)

    # Auto-seed if brand new database with no accounts
    if len(tracker.get_all_accounts()) == 0 or args.seed:
        print("[INFO] Seeding sample financial records into database...")
        seed_sample_data(tracker)
        print("[OK] Seeding complete.")

    if args.report:
        report_output = tracker.generate_report(args.report)
        print(report_output)
        return

    if args.cli:
        run_interactive_cli(tracker)
        return

    if args.gui:
        try:
            from gui import launch_gui
            launch_gui(tracker)
            return
        except Exception as e:
            print(f"[WARN] Unable to launch Tkinter GUI ({e}). Falling back to CLI mode.")
            run_interactive_cli(tracker)
            return

    # Default action: check if DISPLAY is available, otherwise show summary & CLI
    display_var = os.environ.get("DISPLAY")
    if display_var:
        try:
            from gui import launch_gui
            launch_gui(tracker)
        except Exception:
            run_interactive_cli(tracker)
    else:
        # Running in headless container or standard CLI
        print(tracker.generate_report("text"))
        print("\nNote: Running in headless environment (no X11 DISPLAY detected).")
        print("Run with '--cli' for interactive CLI mode, '--report html' for HTML export, or '--test' for automated test suite.")


if __name__ == "__main__":
    main()

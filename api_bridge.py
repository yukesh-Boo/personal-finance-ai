"""API Bridge connecting web backend directly to Python FinanceTracker engine."""

import sys
import json
import os
import zipfile
import io
from decimal import Decimal
from finance_tracker import FinanceTracker
from sample_data import seed_sample_data
from exceptions import FinanceTrackerError


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        sys.exit(1)

    action = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else "finance_tracker.db"
    tracker = FinanceTracker(db_path=db_path)

    # Read payload from sys.argv[3] if passed
    payload = {}
    if len(sys.argv) > 3:
        try:
            payload = json.loads(sys.argv[3])
        except Exception:
            payload = {}

    try:
        if action == "bootstrap":
            dossier = tracker.get_analytics_dossier()
            txns = tracker.get_transactions(limit=payload.get("limit", 200))
            print(json.dumps({"success": True, "data": {"dossier": dossier, "transactions": txns}}))

        elif action == "dossier":
            dossier = tracker.get_analytics_dossier()
            print(json.dumps({"success": True, "data": dossier}))

        elif action == "transactions":
            txns = tracker.get_transactions(
                account_id=payload.get("account_id"),
                category=payload.get("category"),
                start_date=payload.get("start_date"),
                end_date=payload.get("end_date"),
                txn_type=payload.get("txn_type"),
                search_query=payload.get("search_query"),
                limit=payload.get("limit"),
            )
            print(json.dumps({"success": True, "data": txns}))

        elif action == "add_transaction":
            txn = tracker.add_transaction(
                amount=payload["amount"],
                transaction_type=payload["type"],
                category=payload["category"],
                account_id=payload["account_id"],
                date_str=payload.get("date"),
                description=payload.get("description", ""),
                payment_method=payload.get("payment_method", "Bank Transfer"),
                recurring=payload.get("recurring", "none"),
                target_account_id=payload.get("target_account_id"),
            )
            print(json.dumps({"success": True, "data": txn.to_dict()}))

        elif action == "transfer":
            txn = tracker.transfer(
                from_account_id=payload["from_account_id"],
                to_account_id=payload["to_account_id"],
                amount=payload["amount"],
                date_str=payload.get("date"),
                description=payload.get("description", "Account Transfer"),
            )
            print(json.dumps({"success": True, "data": txn.to_dict()}))

        elif action == "delete_transaction":
            tracker.delete_transaction(payload["id"])
            print(json.dumps({"success": True, "message": "Transaction deleted"}))

        elif action == "add_account":
            acc = tracker.add_account(
                name=payload["name"],
                account_type=payload.get("type", "checking"),
                initial_balance=Decimal(str(payload.get("initial_balance", "0.00"))),
                currency=payload.get("currency", "USD"),
                allow_overdraft=bool(payload.get("allow_overdraft", False)),
            )
            print(json.dumps({"success": True, "data": acc.to_dict()}))

        elif action == "set_budget":
            b = tracker.set_budget(
                category=payload["category"],
                limit_amount=payload["limit"],
                period=payload.get("period", "monthly"),
                period_key=payload.get("period_key"),
            )
            print(json.dumps({"success": True, "data": b.to_dict()}))

        elif action == "seed":
            seed_sample_data(tracker)
            print(json.dumps({"success": True, "message": "Sample data seeded"}))

        elif action == "report":
            fmt = payload.get("format", "text")
            report_text = tracker.generate_report(fmt)
            print(json.dumps({"success": True, "format": fmt, "content": report_text}))

        elif action == "source_files":
            files_to_read = [
                "main.py",
                "finance_tracker.py",
                "account.py",
                "transaction.py",
                "budget.py",
                "database.py",
                "analytics.py",
                "reports.py",
                "validators.py",
                "exceptions.py",
                "sample_data.py",
                "gui.py",
                "requirements.txt",
                "README.md",
                "tests/test_finance_tracker.py",
                "tests/test_analytics.py",
                "tests/test_budget.py",
                "tests/test_database.py",
            ]
            file_map = {}
            for fname in files_to_read:
                if os.path.exists(fname):
                    with open(fname, "r", encoding="utf-8") as f:
                        file_map[fname] = f.read()
            print(json.dumps({"success": True, "files": file_map}))

        elif action == "make_zip":
            # Creates python_project.zip in current directory
            files = [
                "main.py", "finance_tracker.py", "account.py", "transaction.py",
                "budget.py", "database.py", "analytics.py", "reports.py",
                "validators.py", "exceptions.py", "sample_data.py", "gui.py",
                "requirements.txt", "README.md", "tests/__init__.py",
                "tests/test_finance_tracker.py", "tests/test_analytics.py",
                "tests/test_budget.py", "tests/test_database.py"
            ]
            zip_path = "smart_finance_tracker_python.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
                for fpath in files:
                    if os.path.exists(fpath):
                        z.write(fpath)
            print(json.dumps({"success": True, "zip_path": zip_path}))

        else:
            print(json.dumps({"success": False, "error": f"Unknown action: {action}"}))

    except FinanceTrackerError as e:
        print(json.dumps({"success": False, "error": str(e), "code": e.code}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()

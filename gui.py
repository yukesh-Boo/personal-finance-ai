"""Graphical User Interface implementation using Tkinter and Matplotlib.

Features an tabbed layout, financial dashboard, transaction ledger with
search/filters, category manager, interactive budget cards, and Matplotlib chart integration.
"""

import sys
import os
from decimal import Decimal
from datetime import datetime
from typing import Optional

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

from finance_tracker import FinanceTracker
from exceptions import FinanceTrackerError


class FinanceTrackerGUI:
    """Tkinter graphical application for Personal Finance Tracker."""

    def __init__(self, tracker: Optional[FinanceTracker] = None, root: Optional[Any] = None):
        if not TKINTER_AVAILABLE:
            raise RuntimeError("Tkinter is not installed or GUI display environment is unavailable.")

        self.tracker = tracker or FinanceTracker()
        self.root = root or tk.Tk()
        self.root.title("Smart Personal Finance Tracker")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)

        # Style configuration
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self._configure_styles()
        self._build_layout()
        self.refresh_all_data()

    def _configure_styles(self) -> None:
        self.style.configure(".", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), foreground="#0f172a")
        self.style.configure("MetricVal.TLabel", font=("Helvetica", 18, "bold"), foreground="#047857")
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#f1f5f9")
        self.style.configure("Accent.TButton", font=("Helvetica", 10, "bold"))

    def _build_layout(self) -> None:
        # Top Header Bar
        top_bar = ttk.Frame(self.root, padding=(16, 12))
        top_bar.pack(fill=tk.X)

        title_lbl = ttk.Label(top_bar, text="Smart Personal Finance Tracker", style="Header.TLabel")
        title_lbl.pack(side=tk.LEFT)

        btn_box = ttk.Frame(top_bar)
        btn_box.pack(side=tk.RIGHT)

        ttk.Button(btn_box, text="Refresh Data", command=self.refresh_all_data).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="Export Report", command=self.export_report).pack(side=tk.LEFT, padx=4)

        # Main Notebook Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # Tabs
        self.tab_dashboard = ttk.Frame(self.notebook, padding=12)
        self.tab_transactions = ttk.Frame(self.notebook, padding=12)
        self.tab_budgets = ttk.Frame(self.notebook, padding=12)
        self.tab_analytics = ttk.Frame(self.notebook, padding=12)
        self.tab_accounts = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.tab_dashboard, text=" Dashboard ")
        self.notebook.add(self.tab_transactions, text=" Transactions ")
        self.notebook.add(self.tab_budgets, text=" Budgets ")
        self.notebook.add(self.tab_analytics, text=" Analytics & Charts ")
        self.notebook.add(self.tab_accounts, text=" Accounts & Settings ")

        self._build_dashboard_tab()
        self._build_transactions_tab()
        self._build_budgets_tab()
        self._build_analytics_tab()
        self._build_accounts_tab()

    # --- 1. Dashboard Tab ---
    def _build_dashboard_tab(self) -> None:
        metrics_frame = ttk.LabelFrame(self.tab_dashboard, text=" Financial Overview ", padding=16)
        metrics_frame.pack(fill=tk.X, pady=(0, 12))

        self.lbl_total_assets = ttk.Label(metrics_frame, text="Total Balance: $0.00", font=("Helvetica", 14, "bold"))
        self.lbl_total_assets.grid(row=0, column=0, padx=20, sticky="w")

        self.lbl_income = ttk.Label(metrics_frame, text="Income: $0.00", foreground="#16a34a", font=("Helvetica", 12))
        self.lbl_income.grid(row=0, column=1, padx=20, sticky="w")

        self.lbl_expenses = ttk.Label(metrics_frame, text="Expenses: $0.00", foreground="#dc2626", font=("Helvetica", 12))
        self.lbl_expenses.grid(row=0, column=2, padx=20, sticky="w")

        self.lbl_savings = ttk.Label(metrics_frame, text="Net Savings: $0.00", font=("Helvetica", 12))
        self.lbl_savings.grid(row=0, column=3, padx=20, sticky="w")

        self.lbl_health = ttk.Label(metrics_frame, text="Health Score: 0/100", font=("Helvetica", 12, "bold"))
        self.lbl_health.grid(row=0, column=4, padx=20, sticky="w")

        # Quick Add Transaction Form
        quick_frame = ttk.LabelFrame(self.tab_dashboard, text=" Quick Add Transaction ", padding=14)
        quick_frame.pack(fill=tk.X, pady=(0, 12))

        # Fields: Type, Amount, Category, Account, Description
        ttk.Label(quick_frame, text="Type:").grid(row=0, column=0, padx=4, sticky="w")
        self.dash_type_var = tk.StringVar(value="expense")
        type_cb = ttk.Combobox(quick_frame, textvariable=self.dash_type_var, values=["expense", "income", "transfer"], width=10, state="readonly")
        type_cb.grid(row=0, column=1, padx=4)

        ttk.Label(quick_frame, text="Amount:").grid(row=0, column=2, padx=4, sticky="w")
        self.dash_amount_var = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.dash_amount_var, width=12).grid(row=0, column=3, padx=4)

        ttk.Label(quick_frame, text="Category:").grid(row=0, column=4, padx=4, sticky="w")
        self.dash_cat_var = tk.StringVar(value="Groceries")
        self.dash_cat_cb = ttk.Combobox(quick_frame, textvariable=self.dash_cat_var, width=16)
        self.dash_cat_cb.grid(row=0, column=5, padx=4)

        ttk.Label(quick_frame, text="Account:").grid(row=0, column=6, padx=4, sticky="w")
        self.dash_acc_var = tk.StringVar()
        self.dash_acc_cb = ttk.Combobox(quick_frame, textvariable=self.dash_acc_var, width=16, state="readonly")
        self.dash_acc_cb.grid(row=0, column=7, padx=4)

        ttk.Label(quick_frame, text="Description:").grid(row=1, column=0, padx=4, pady=6, sticky="w")
        self.dash_desc_var = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.dash_desc_var, width=32).grid(row=1, column=1, columnspan=3, padx=4, pady=6, sticky="w")

        ttk.Button(quick_frame, text="Submit Transaction", command=self.quick_add_transaction).grid(row=1, column=6, columnspan=2, padx=4, pady=6, sticky="e")

        # Recent Transactions Mini-Ledger
        recent_frame = ttk.LabelFrame(self.tab_dashboard, text=" Recent Transactions ", padding=8)
        recent_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("date", "type", "category", "amount", "account", "description")
        self.tree_recent = ttk.Treeview(recent_frame, columns=cols, show="headings", height=8)
        for col in cols:
            self.tree_recent.heading(col, text=col.title())
            self.tree_recent.column(col, width=130)
        self.tree_recent.pack(fill=tk.BOTH, expand=True)

    # --- 2. Transactions Tab ---
    def _build_transactions_tab(self) -> None:
        # Search & Filter controls
        filter_bar = ttk.Frame(self.tab_transactions, padding=(0, 0, 0, 8))
        filter_bar.pack(fill=tk.X)

        ttk.Label(filter_bar, text="Search:").pack(side=tk.LEFT, padx=4)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_bar, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=4)
        ttk.Button(filter_bar, text="Search", command=self.apply_transaction_filters).pack(side=tk.LEFT, padx=4)

        ttk.Label(filter_bar, text="Type:").pack(side=tk.LEFT, padx=(12, 4))
        self.filter_type_var = tk.StringVar(value="All")
        type_filter = ttk.Combobox(filter_bar, textvariable=self.filter_type_var, values=["All", "income", "expense", "transfer"], width=10, state="readonly")
        type_filter.pack(side=tk.LEFT, padx=4)
        type_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_transaction_filters())

        ttk.Button(filter_bar, text="Delete Selected", command=self.delete_selected_transaction).pack(side=tk.RIGHT, padx=4)
        ttk.Button(filter_bar, text="Reset Filters", command=self.reset_transaction_filters).pack(side=tk.RIGHT, padx=4)

        # Full Ledger Treeview
        tree_frame = ttk.Frame(self.tab_transactions)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "date", "type", "category", "amount", "account", "payment_method", "description")
        self.tree_full = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for col in cols:
            self.tree_full.heading(col, text=col.replace("_", " ").title())
            self.tree_full.column(col, width=120)
        self.tree_full.column("id", width=110)
        self.tree_full.column("description", width=220)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_full.yview)
        self.tree_full.configure(yscroll=scrollbar.set)
        self.tree_full.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # --- 3. Budgets Tab ---
    def _build_budgets_tab(self) -> None:
        top_ctrl = ttk.Frame(self.tab_budgets, padding=(0, 0, 0, 8))
        top_ctrl.pack(fill=tk.X)

        ttk.Label(top_ctrl, text="Configure Budget - Category:").pack(side=tk.LEFT, padx=4)
        self.b_cat_var = tk.StringVar()
        self.b_cat_cb = ttk.Combobox(top_ctrl, textvariable=self.b_cat_var, width=16)
        self.b_cat_cb.pack(side=tk.LEFT, padx=4)

        ttk.Label(top_ctrl, text="Limit ($):").pack(side=tk.LEFT, padx=4)
        self.b_limit_var = tk.StringVar()
        ttk.Entry(top_ctrl, textvariable=self.b_limit_var, width=12).pack(side=tk.LEFT, padx=4)

        ttk.Button(top_ctrl, text="Save Budget", command=self.save_budget).pack(side=tk.LEFT, padx=8)

        # Budget Table
        cols = ("category", "spent", "limit", "utilization", "status", "overrun")
        self.tree_budgets = ttk.Treeview(self.tab_budgets, columns=cols, show="headings", height=12)
        for col in cols:
            self.tree_budgets.heading(col, text=col.title())
            self.tree_budgets.column(col, width=130)
        self.tree_budgets.pack(fill=tk.BOTH, expand=True)

    # --- 4. Analytics & Charts Tab ---
    def _build_analytics_tab(self) -> None:
        self.analytics_frame = ttk.Frame(self.tab_analytics)
        self.analytics_frame.pack(fill=tk.BOTH, expand=True)

        self.insights_text = tk.Text(self.analytics_frame, height=10, font=("Courier", 10), bg="#f8fafc")
        self.insights_text.pack(fill=tk.X, pady=(0, 8))

        self.chart_container = ttk.Frame(self.analytics_frame)
        self.chart_container.pack(fill=tk.BOTH, expand=True)

    # --- 5. Accounts Tab ---
    def _build_accounts_tab(self) -> None:
        acc_form = ttk.LabelFrame(self.tab_accounts, text=" Create New Account ", padding=14)
        acc_form.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(acc_form, text="Name:").grid(row=0, column=0, padx=4)
        self.new_acc_name = tk.StringVar()
        ttk.Entry(acc_form, textvariable=self.new_acc_name, width=20).grid(row=0, column=1, padx=4)

        ttk.Label(acc_form, text="Type:").grid(row=0, column=2, padx=4)
        self.new_acc_type = tk.StringVar(value="checking")
        ttk.Combobox(acc_form, textvariable=self.new_acc_type, values=["checking", "savings", "cash", "investment"], state="readonly", width=12).grid(row=0, column=3, padx=4)

        ttk.Label(acc_form, text="Initial Balance:").grid(row=0, column=4, padx=4)
        self.new_acc_bal = tk.StringVar(value="0.00")
        ttk.Entry(acc_form, textvariable=self.new_acc_bal, width=10).grid(row=0, column=5, padx=4)

        ttk.Button(acc_form, text="Add Account", command=self.create_account_action).grid(row=0, column=6, padx=8)

        # Accounts list
        cols = ("id", "name", "type", "currency", "balance")
        self.tree_accounts = ttk.Treeview(self.tab_accounts, columns=cols, show="headings", height=8)
        for col in cols:
            self.tree_accounts.heading(col, text=col.title())
            self.tree_accounts.column(col, width=140)
        self.tree_accounts.pack(fill=tk.BOTH, expand=True)

    # --- Data Synchronization ---
    def refresh_all_data(self) -> None:
        """Fetches latest data and updates all UI tabs."""
        dossier = self.tracker.get_analytics_dossier()
        accounts = self.tracker.get_all_accounts()
        categories = self.tracker.db.get_categories()

        cat_names = [c["name"] for c in categories]
        self.dash_cat_cb["values"] = cat_names
        self.b_cat_cb["values"] = cat_names

        acc_names = [a.name for a in accounts]
        self.dash_acc_cb["values"] = acc_names
        if acc_names and not self.dash_acc_var.get():
            self.dash_acc_var.set(acc_names[0])

        # Summary Metrics
        summary = dossier["summary"]
        total_assets = sum(a.balance for a in accounts)
        self.lbl_total_assets.config(text=f"Total Balance: ${total_assets:,.2f}")
        self.lbl_income.config(text=f"Income: ${Decimal(summary['total_income']):,.2f}")
        self.lbl_expenses.config(text=f"Expenses: ${Decimal(summary['total_expenses']):,.2f}")
        self.lbl_savings.config(text=f"Net Savings: ${Decimal(summary['net_savings']):,.2f} ({summary['savings_rate_pct']}%)")
        self.lbl_health.config(text=f"Health: {dossier['financial_health']['score']}/100 ({dossier['financial_health']['rating']})")

        # Populate Recent
        self.tree_recent.delete(*self.tree_recent.get_children())
        txns = self.tracker.get_transactions(limit=12)
        acc_dict = {a.id: a.name for a in accounts}
        for t in txns:
            self.tree_recent.insert(
                "",
                tk.END,
                values=(
                    t["date"],
                    t["type"],
                    t["category"],
                    f"${Decimal(t['amount']):,.2f}",
                    acc_dict.get(t["account_id"], t["account_id"]),
                    t.get("description", ""),
                ),
            )

        # Populate Full
        self.populate_full_ledger(self.tracker.get_transactions())

        # Populate Budgets
        self.tree_budgets.delete(*self.tree_budgets.get_children())
        for b in dossier["budget_evaluations"]:
            self.tree_budgets.insert(
                "",
                tk.END,
                values=(
                    b["category"],
                    f"${Decimal(b['actual_spent']):,.2f}",
                    f"${Decimal(b['effective_limit']):,.2f}",
                    f"{b['utilization_percentage']}%",
                    b["status"],
                    f"${Decimal(b['overrun_amount']):,.2f}",
                ),
            )

        # Populate Accounts
        self.tree_accounts.delete(*self.tree_accounts.get_children())
        for a in accounts:
            self.tree_accounts.insert("", tk.END, values=(a.id, a.name, a.account_type.value, a.currency, f"${a.balance:,.2f}"))

        # Analytics Text & Charts
        self.insights_text.delete("1.0", tk.END)
        self.insights_text.insert(tk.END, self.tracker.generate_report("text"))

        if MATPLOTLIB_AVAILABLE:
            self._render_matplotlib_chart(dossier["category_breakdown"])

    def populate_full_ledger(self, transactions: list) -> None:
        self.tree_full.delete(*self.tree_full.get_children())
        acc_dict = {a.id: a.name for a in self.tracker.get_all_accounts()}
        for t in transactions:
            self.tree_full.insert(
                "",
                tk.END,
                values=(
                    t["id"],
                    t["date"],
                    t["type"],
                    t["category"],
                    f"${Decimal(t['amount']):,.2f}",
                    acc_dict.get(t["account_id"], t["account_id"]),
                    t.get("payment_method", ""),
                    t.get("description", ""),
                ),
            )

    def _render_matplotlib_chart(self, category_breakdown: list) -> None:
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        if not category_breakdown:
            return

        fig = Figure(figsize=(7, 3.5), dpi=100)
        ax = fig.add_subplot(111)

        labels = [c["category"] for c in category_breakdown[:6]]
        values = [float(c["amount"]) for c in category_breakdown[:6]]

        ax.bar(labels, values, color="#3b82f6")
        ax.set_title("Top Spending Categories ($)")
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # --- Actions ---
    def quick_add_transaction(self) -> None:
        try:
            amt = self.dash_amount_var.get()
            ttype = self.dash_type_var.get()
            cat = self.dash_cat_var.get()
            acc_name = self.dash_acc_var.get()
            desc = self.dash_desc_var.get()

            acc = self.tracker.get_account(acc_name)
            self.tracker.add_transaction(
                amount=amt,
                transaction_type=ttype,
                category=cat,
                account_id=acc.id,
                description=desc,
            )
            self.dash_amount_var.set("")
            self.dash_desc_var.set("")
            self.refresh_all_data()
            messagebox.showinfo("Success", "Transaction recorded successfully.")
        except FinanceTrackerError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))

    def apply_transaction_filters(self) -> None:
        search = self.search_var.get()
        ttype = self.filter_type_var.get()
        filtered = self.tracker.get_transactions(
            txn_type=ttype if ttype != "All" else None,
            search_query=search if search else None,
        )
        self.populate_full_ledger(filtered)

    def reset_transaction_filters(self) -> None:
        self.search_var.set("")
        self.filter_type_var.set("All")
        self.populate_full_ledger(self.tracker.get_transactions())

    def delete_selected_transaction(self) -> None:
        selected = self.tree_full.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a transaction to delete.")
            return

        item = self.tree_full.item(selected[0])
        txn_id = item["values"][0]

        if messagebox.askyesno("Confirm Deletion", f"Permanently delete transaction {txn_id}?"):
            try:
                self.tracker.delete_transaction(txn_id)
                self.refresh_all_data()
                messagebox.showinfo("Deleted", f"Transaction {txn_id} removed.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def save_budget(self) -> None:
        try:
            cat = self.b_cat_var.get()
            limit = self.b_limit_var.get()
            self.tracker.set_budget(cat, limit)
            self.b_limit_var.set("")
            self.refresh_all_data()
            messagebox.showinfo("Saved", f"Budget for '{cat}' updated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_account_action(self) -> None:
        try:
            name = self.new_acc_name.get()
            atype = self.new_acc_type.get()
            bal = self.new_acc_bal.get()
            self.tracker.add_account(name=name, account_type=atype, initial_balance=bal)
            self.new_acc_name.set("")
            self.refresh_all_data()
            messagebox.showinfo("Created", f"Account '{name}' created.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_csv(self) -> None:
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filepath:
            data = self.tracker.generate_report("csv")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(data)
            messagebox.showinfo("Exported", f"Saved to {filepath}")

    def export_report(self) -> None:
        filepath = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])
        if filepath:
            html = self.tracker.generate_report("html")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            messagebox.showinfo("Exported", f"Report saved to {filepath}")


def launch_gui(tracker: Optional[FinanceTracker] = None) -> None:
    """Entry point for Tkinter GUI execution."""
    root = tk.Tk()
    FinanceTrackerGUI(tracker=tracker, root=root)
    root.mainloop()

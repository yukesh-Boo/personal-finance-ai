import React from "react";
import {
  Wallet,
  PlusCircle,
  ArrowLeftRight,
  Database,
  Terminal,
  FileText,
  Code2,
  RefreshCw,
} from "lucide-react";

interface HeaderProps {
  onOpenAddTransaction: () => void;
  onOpenTransfer: () => void;
  onOpenTestRunner: () => void;
  onOpenCodeInspector: () => void;
  onOpenReport: () => void;
  onSeedData: () => void;
  isSeeding: boolean;
  activeTab: "overview" | "transactions" | "budgets" | "analytics";
  setActiveTab: (tab: "overview" | "transactions" | "budgets" | "analytics") => void;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenAddTransaction,
  onOpenTransfer,
  onOpenTestRunner,
  onOpenCodeInspector,
  onOpenReport,
  onSeedData,
  isSeeding,
  activeTab,
  setActiveTab,
}) => {
  return (
    <header className="border-b border-slate-200 bg-white sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between py-4 gap-4">
          {/* Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center shadow-sm">
              <Wallet className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-bold tracking-tight text-slate-900">
                  Smart Personal Finance Tracker
                </h1>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800">
                  Python + SQLite + OOP
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                ACID Persistence • Dynamic Balance Reconciliation • Statistical Anomaly Detection
              </p>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              id="btn-run-tests"
              onClick={onOpenTestRunner}
              className="inline-flex items-center px-3 py-2 text-xs font-medium rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors shadow-2xs"
              title="Run 22 Python automated unit tests"
            >
              <Terminal className="w-3.5 h-3.5 mr-1.5 text-indigo-600" />
              Python Tests (22)
            </button>

            <button
              id="btn-inspect-code"
              onClick={onOpenCodeInspector}
              className="inline-flex items-center px-3 py-2 text-xs font-medium rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors shadow-2xs"
              title="Inspect Python source code & download ZIP"
            >
              <Code2 className="w-3.5 h-3.5 mr-1.5 text-blue-600" />
              Source Code
            </button>

            <button
              id="btn-view-report"
              onClick={onOpenReport}
              className="inline-flex items-center px-3 py-2 text-xs font-medium rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors shadow-2xs"
            >
              <FileText className="w-3.5 h-3.5 mr-1.5 text-slate-600" />
              Reports
            </button>

            <button
              id="btn-seed-sample"
              onClick={onSeedData}
              disabled={isSeeding}
              className="inline-flex items-center px-3 py-2 text-xs font-medium rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors disabled:opacity-50 shadow-2xs"
              title="Reset and seed multi-month sample database"
            >
              <Database className={`w-3.5 h-3.5 mr-1.5 text-amber-600 ${isSeeding ? "animate-spin" : ""}`} />
              {isSeeding ? "Seeding..." : "Seed Data"}
            </button>

            <button
              id="btn-transfer-funds"
              onClick={onOpenTransfer}
              className="inline-flex items-center px-3 py-2 text-xs font-medium rounded-lg text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 transition-colors shadow-2xs"
            >
              <ArrowLeftRight className="w-3.5 h-3.5 mr-1.5 text-indigo-600" />
              Transfer
            </button>

            <button
              id="btn-add-transaction"
              onClick={onOpenAddTransaction}
              className="inline-flex items-center px-3.5 py-2 text-xs font-semibold rounded-lg text-white bg-slate-900 hover:bg-slate-800 transition-colors shadow-xs"
            >
              <PlusCircle className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
              Add Transaction
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-t border-slate-100 pt-1 -mb-px space-x-6">
          <button
            id="tab-overview"
            onClick={() => setActiveTab("overview")}
            className={`py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "overview"
                ? "border-emerald-600 text-emerald-700"
                : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
            }`}
          >
            Overview & Balance
          </button>
          <button
            id="tab-transactions"
            onClick={() => setActiveTab("transactions")}
            className={`py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "transactions"
                ? "border-emerald-600 text-emerald-700"
                : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
            }`}
          >
            Ledger & Transactions
          </button>
          <button
            id="tab-budgets"
            onClick={() => setActiveTab("budgets")}
            className={`py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "budgets"
                ? "border-emerald-600 text-emerald-700"
                : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
            }`}
          >
            Budgets & Overruns
          </button>
          <button
            id="tab-analytics"
            onClick={() => setActiveTab("analytics")}
            className={`py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "analytics"
                ? "border-emerald-600 text-emerald-700"
                : "border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300"
            }`}
          >
            Analytics & Forecasting
          </button>
        </div>
      </div>
    </header>
  );
};

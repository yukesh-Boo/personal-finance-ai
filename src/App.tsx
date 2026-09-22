import React, { useState, useEffect, useCallback } from "react";
import { Header } from "./components/Header";
import { MetricsOverview } from "./components/MetricsOverview";
import { AccountsList } from "./components/AccountsList";
import { BudgetsManager } from "./components/BudgetsManager";
import { TransactionsTable } from "./components/TransactionsTable";
import { AnalyticsPanel } from "./components/AnalyticsPanel";
import { TestRunnerModal } from "./components/TestRunnerModal";
import { CodeInspectorModal } from "./components/CodeInspectorModal";
import { ReportModal } from "./components/ReportModal";
import { FinancialDossier, TransactionData } from "./types";
import { RefreshCw, AlertCircle } from "lucide-react";

export default function App() {
  const [dossier, setDossier] = useState<FinancialDossier | null>(null);
  const [transactions, setTransactions] = useState<TransactionData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSeeding, setIsSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "transactions" | "budgets" | "analytics">("overview");

  // Modals
  const [isAddTxnOpen, setIsAddTxnOpen] = useState(false);
  const [isTransferOpen, setIsTransferOpen] = useState(false);
  const [isTestRunnerOpen, setIsTestRunnerOpen] = useState(false);
  const [isCodeInspectorOpen, setIsCodeInspectorOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);

  const fetchDossierAndTransactions = useCallback(async () => {
    try {
      setError(null);
      const [dossierRes, txnsRes] = await Promise.all([
        fetch("/api/finance/dossier"),
        fetch("/api/finance/transactions?limit=200"),
      ]);

      const dossierData = await dossierRes.json();
      const txnsData = await txnsRes.json();

      if (dossierData.success && dossierData.data) {
        setDossier(dossierData.data);
      } else {
        throw new Error(dossierData.error || "Failed to load financial summary");
      }

      if (txnsData.success && txnsData.data) {
        setTransactions(txnsData.data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to connect to backend engine.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDossierAndTransactions();
  }, [fetchDossierAndTransactions]);

  const handleAddTransaction = async (txn: any) => {
    const res = await fetch("/api/finance/transactions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(txn),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Failed to add transaction");
    await fetchDossierAndTransactions();
  };

  const handleTransfer = async (transferData: any) => {
    const res = await fetch("/api/finance/transfer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(transferData),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Transfer failed");
    await fetchDossierAndTransactions();
  };

  const handleDeleteTransaction = async (id: string) => {
    if (!confirm("Are you sure you want to delete this transaction? Balance will be reconciled automatically.")) {
      return;
    }
    const res = await fetch("/api/finance/delete-transaction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    const data = await res.json();
    if (!data.success) alert(data.error || "Failed to delete transaction");
    await fetchDossierAndTransactions();
  };

  const handleAddAccount = async (accountData: any) => {
    const res = await fetch("/api/finance/accounts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(accountData),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Failed to create account");
    await fetchDossierAndTransactions();
  };

  const handleSetBudget = async (budgetData: any) => {
    const res = await fetch("/api/finance/budgets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(budgetData),
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Failed to configure budget");
    await fetchDossierAndTransactions();
  };

  const handleSeedData = async () => {
    if (!confirm("Re-seed the SQLite database with multi-month realistic financial history?")) {
      return;
    }
    setIsSeeding(true);
    try {
      const res = await fetch("/api/finance/seed", { method: "POST" });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || "Failed to seed sample data");
      await fetchDossierAndTransactions();
    } catch (err: any) {
      alert(`Error seeding data: ${err.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/70 text-slate-900 flex flex-col font-sans">
      {/* Sticky Navigation Header */}
      <Header
        onOpenAddTransaction={() => setIsAddTxnOpen(true)}
        onOpenTransfer={() => setIsTransferOpen(true)}
        onOpenTestRunner={() => setIsTestRunnerOpen(true)}
        onOpenCodeInspector={() => setIsCodeInspectorOpen(true)}
        onOpenReport={() => setIsReportOpen(true)}
        onSeedData={handleSeedData}
        isSeeding={isSeeding}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-3">
            <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin" />
            <span className="text-sm font-medium text-slate-600">
              Connecting to Python Engine & Loading Financial Records...
            </span>
          </div>
        ) : error ? (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 text-center max-w-md mx-auto my-12">
            <AlertCircle className="w-8 h-8 text-rose-600 mx-auto mb-2" />
            <h3 className="text-sm font-bold text-rose-900 mb-1">
              Backend Initialization Error
            </h3>
            <p className="text-xs text-rose-700 mb-4">{error}</p>
            <button
              onClick={() => fetchDossierAndTransactions()}
              className="px-4 py-2 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 rounded-lg transition-colors"
            >
              Retry Connection
            </button>
          </div>
        ) : dossier ? (
          <div className="space-y-8">
            {activeTab === "overview" && (
              <>
                <MetricsOverview dossier={dossier} />
                <AccountsList
                  accounts={dossier.accounts}
                  onAddAccount={handleAddAccount}
                />
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <BudgetsManager
                    budgets={dossier.budget_evaluations}
                    onSetBudget={handleSetBudget}
                  />
                  <div className="space-y-6">
                    <AnalyticsPanel dossier={dossier} />
                  </div>
                </div>
              </>
            )}

            {activeTab === "transactions" && (
              <TransactionsTable
                transactions={transactions}
                accounts={dossier.accounts}
                onAddTransaction={handleAddTransaction}
                onTransfer={handleTransfer}
                onDeleteTransaction={handleDeleteTransaction}
                isAddModalOpen={isAddTxnOpen}
                setIsAddModalOpen={setIsAddTxnOpen}
                isTransferModalOpen={isTransferOpen}
                setIsTransferModalOpen={setIsTransferOpen}
              />
            )}

            {activeTab === "budgets" && (
              <div className="space-y-6">
                <BudgetsManager
                  budgets={dossier.budget_evaluations}
                  onSetBudget={handleSetBudget}
                />
              </div>
            )}

            {activeTab === "analytics" && (
              <div className="space-y-6">
                <AnalyticsPanel dossier={dossier} />
              </div>
            )}
          </div>
        ) : null}
      </main>

      {/* Modals */}
      <TestRunnerModal
        isOpen={isTestRunnerOpen}
        onClose={() => setIsTestRunnerOpen(false)}
      />

      <CodeInspectorModal
        isOpen={isCodeInspectorOpen}
        onClose={() => setIsCodeInspectorOpen(false)}
      />

      <ReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
      />

      {/* Global Quick Action Modals if triggered from Header when on another tab */}
      {isAddTxnOpen && activeTab !== "transactions" && dossier && (
        <TransactionsTable
          transactions={transactions}
          accounts={dossier.accounts}
          onAddTransaction={handleAddTransaction}
          onTransfer={handleTransfer}
          onDeleteTransaction={handleDeleteTransaction}
          isAddModalOpen={isAddTxnOpen}
          setIsAddModalOpen={setIsAddTxnOpen}
          isTransferModalOpen={isTransferOpen}
          setIsTransferModalOpen={setIsTransferOpen}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            Smart Personal Finance Tracker • Python Standard Library + SQLite3 + Tkinter + React Web UI
          </span>
          <span className="font-mono text-slate-400">
            SOLID Architecture • Decimal Quantization • ACID Concurrency
          </span>
        </div>
      </footer>
    </div>
  );
}

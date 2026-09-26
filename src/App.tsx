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
import { apiGet, apiPost } from "./utils/api";

export default function App() {
  const [dossier, setDossier] = useState<FinancialDossier | null>(() => {
    try {
      const cached = sessionStorage.getItem("fin_dossier_cache");
      return cached ? JSON.parse(cached) : null;
    } catch {
      return null;
    }
  });
  const [transactions, setTransactions] = useState<TransactionData[]>(() => {
    try {
      const cached = sessionStorage.getItem("fin_txns_cache");
      return cached ? JSON.parse(cached) : [];
    } catch {
      return [];
    }
  });
  const [isLoading, setIsLoading] = useState(() => {
    try {
      return !sessionStorage.getItem("fin_dossier_cache");
    } catch {
      return true;
    }
  });
  const [isSeeding, setIsSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "transactions" | "budgets" | "analytics">("overview");

  // Modals
  const [isAddTxnOpen, setIsAddTxnOpen] = useState(false);
  const [isTransferOpen, setIsTransferOpen] = useState(false);
  const [isTestRunnerOpen, setIsTestRunnerOpen] = useState(false);
  const [isCodeInspectorOpen, setIsCodeInspectorOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState<{
    title: string;
    message: string;
    confirmText?: string;
    isDestructive?: boolean;
    onConfirm: () => Promise<void> | void;
  } | null>(null);
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const showToast = (type: "success" | "error", message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4000);
  };

  const fetchDossierAndTransactions = useCallback(async (forceLoading = false) => {
    try {
      if (forceLoading || !dossier) {
        setIsLoading(true);
      }
      setError(null);

      // Fast-path: Unified bootstrap endpoint (1 Python process, 0.1s response)
      try {
        const bootData = await apiGet("/api/finance/bootstrap?limit=200", 2, 5000);
        if (bootData && bootData.success && bootData.data?.dossier) {
          setDossier(bootData.data.dossier);
          if (bootData.data.transactions) {
            setTransactions(bootData.data.transactions);
          }
          try {
            sessionStorage.setItem("fin_dossier_cache", JSON.stringify(bootData.data.dossier));
            if (bootData.data.transactions) {
              sessionStorage.setItem("fin_txns_cache", JSON.stringify(bootData.data.transactions));
            }
          } catch {}
          return;
        }
      } catch (bootErr) {
        console.warn("Fast bootstrap fallback to individual endpoints", bootErr);
      }

      // Fallback path: parallel individual endpoints with safety timeout
      const [dossierData, txnsData] = await Promise.all([
        apiGet("/api/finance/dossier", 2, 6000),
        apiGet("/api/finance/transactions?limit=200", 2, 6000),
      ]);

      if (dossierData && dossierData.success && dossierData.data) {
        setDossier(dossierData.data);
        try {
          sessionStorage.setItem("fin_dossier_cache", JSON.stringify(dossierData.data));
        } catch {}
      } else {
        throw new Error(dossierData?.error || "Failed to load financial summary");
      }

      if (txnsData && txnsData.success && txnsData.data) {
        setTransactions(txnsData.data);
        try {
          sessionStorage.setItem("fin_txns_cache", JSON.stringify(txnsData.data));
        } catch {}
      }
    } catch (err: any) {
      setError(err.message || "Failed to connect to backend engine.");
    } finally {
      setIsLoading(false);
    }
  }, [dossier]);

  const [retryCountdown, setRetryCountdown] = useState<number | null>(null);

  useEffect(() => {
    fetchDossierAndTransactions();
  }, [fetchDossierAndTransactions]);

  // Loading watchdog: never let isLoading linger longer than 7 seconds without user option
  useEffect(() => {
    if (!isLoading) return;
    const timeout = setTimeout(() => {
      if (isLoading && !dossier) {
        setIsLoading(false);
        setError("Connection to Python engine timed out. The backend container may still be warming up.");
      }
    }, 7000);
    return () => clearTimeout(timeout);
  }, [isLoading, dossier]);

  // Auto-retry when backend is waking up or warming up
  useEffect(() => {
    if (!error) {
      setRetryCountdown(null);
      return;
    }

    setRetryCountdown(4);
    const interval = setInterval(() => {
      setRetryCountdown((prev) => {
        if (prev === null || prev <= 1) {
          clearInterval(interval);
          fetchDossierAndTransactions();
          return null;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [error, fetchDossierAndTransactions]);

  const handleAddTransaction = async (txn: any) => {
    const data = await apiPost("/api/finance/transactions", txn);
    if (!data.success) throw new Error(data.error || "Failed to add transaction");
    await fetchDossierAndTransactions();
  };

  const handleTransfer = async (transferData: any) => {
    const data = await apiPost("/api/finance/transfer", transferData);
    if (!data.success) throw new Error(data.error || "Transfer failed");
    await fetchDossierAndTransactions();
  };

  const handleDeleteTransaction = async (id: string): Promise<void> => {
    return new Promise((resolve) => {
      setConfirmDialog({
        title: "Delete Transaction",
        message: "Are you sure you want to delete this transaction? Account balances will be automatically recalculated and reconciled.",
        confirmText: "Delete",
        isDestructive: true,
        onConfirm: async () => {
          try {
            const data = await apiPost("/api/finance/delete-transaction", { id });
            if (!data.success) {
              showToast("error", data.error || "Failed to delete transaction");
            } else {
              showToast("success", "Transaction deleted and balance reconciled.");
            }
            await fetchDossierAndTransactions();
          } catch (err: any) {
            showToast("error", err.message || "Network error deleting transaction");
          } finally {
            resolve();
          }
        },
      });
    });
  };

  const handleAddAccount = async (accountData: any) => {
    const data = await apiPost("/api/finance/accounts", accountData);
    if (!data.success) throw new Error(data.error || "Failed to create account");
    showToast("success", `Account "${accountData.name}" created successfully.`);
    await fetchDossierAndTransactions();
  };

  const handleSetBudget = async (budgetData: any) => {
    const data = await apiPost("/api/finance/budgets", budgetData);
    if (!data.success) throw new Error(data.error || "Failed to configure budget");
    showToast("success", `Budget for ${budgetData.category} updated.`);
    await fetchDossierAndTransactions();
  };

  const handleSeedData = () => {
    setConfirmDialog({
      title: "Re-Seed Financial Database",
      message: "This will reset transactions and seed realistic multi-month data for Checking, Savings, and Cash accounts. Continue?",
      confirmText: "Re-Seed Data",
      isDestructive: false,
      onConfirm: async () => {
        setIsSeeding(true);
        try {
          const data = await apiPost("/api/finance/seed");
          if (!data.success) throw new Error(data.error || "Failed to seed sample data");
          showToast("success", "Sample database seeded with multi-month financial records!");
          await fetchDossierAndTransactions();
        } catch (err: any) {
          showToast("error", `Error seeding data: ${err.message}`);
        } finally {
          setIsSeeding(false);
        }
      },
    });
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
          <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
            <RefreshCw className="w-9 h-9 text-emerald-600 animate-spin" />
            <div className="text-center">
              <p className="text-sm font-semibold text-slate-800">
                Connecting to Python Engine & Loading Financial Records...
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Initializing SQLite persistence and analytics models
              </p>
            </div>
            <button
              onClick={() => fetchDossierAndTransactions(true)}
              className="text-xs text-slate-500 hover:text-emerald-700 underline font-medium pt-2 transition-colors cursor-pointer"
            >
              Taking longer than expected? Click to force reconnect
            </button>
          </div>
        ) : error ? (
          <div className="bg-amber-50/80 border border-amber-200/80 rounded-2xl p-8 text-center max-w-lg mx-auto my-12 shadow-sm">
            <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4 text-amber-700">
              <RefreshCw className="w-6 h-6 animate-spin" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-1">
              Backend Service Warming Up
            </h3>
            <p className="text-sm text-slate-600 mb-5 leading-relaxed">{error}</p>
            {retryCountdown !== null && (
              <p className="text-xs text-amber-800 font-medium mb-4 bg-amber-100/70 py-1.5 px-3 rounded-full inline-block">
                Auto-reconnecting in {retryCountdown}s...
              </p>
            )}
            <div>
              <button
                onClick={() => fetchDossierAndTransactions()}
                className="inline-flex items-center gap-2 px-5 py-2.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl transition-all shadow-xs"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry Connection Now
              </button>
            </div>
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

      {/* Confirmation Dialog Modal */}
      {confirmDialog && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="text-base font-bold text-slate-900 mb-2">
              {confirmDialog.title}
            </h3>
            <p className="text-sm text-slate-600 mb-6 leading-relaxed">
              {confirmDialog.message}
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setConfirmDialog(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  const action = confirmDialog.onConfirm;
                  setConfirmDialog(null);
                  await action();
                }}
                className={`px-4 py-2 text-xs font-semibold rounded-lg text-white transition-colors ${
                  confirmDialog.isDestructive
                    ? "bg-rose-600 hover:bg-rose-700 shadow-xs"
                    : "bg-slate-900 hover:bg-slate-800 shadow-xs"
                }`}
              >
                {confirmDialog.confirmText || "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Toast Notification */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex items-center space-x-2.5 px-4 py-3 rounded-xl shadow-lg border text-xs font-medium transition-all transform animate-in fade-in slide-in-from-bottom-2 ${
            toast.type === "error"
              ? "bg-rose-50 border-rose-200 text-rose-800"
              : "bg-emerald-50 border-emerald-200 text-emerald-800"
          }`}
        >
          <span>{toast.message}</span>
        </div>
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

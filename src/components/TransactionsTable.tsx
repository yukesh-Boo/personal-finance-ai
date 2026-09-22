import React, { useState, useMemo } from "react";
import {
  Search,
  Filter,
  Plus,
  ArrowLeftRight,
  Trash2,
  Calendar,
  Tag,
  CreditCard,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { TransactionData, AccountData } from "../types";

interface TransactionsTableProps {
  transactions: TransactionData[];
  accounts: AccountData[];
  onAddTransaction: (txn: any) => Promise<void>;
  onTransfer: (data: any) => Promise<void>;
  onDeleteTransaction: (id: string) => Promise<void>;
  isAddModalOpen: boolean;
  setIsAddModalOpen: (val: boolean) => void;
  isTransferModalOpen: boolean;
  setIsTransferModalOpen: (val: boolean) => void;
}

export const TransactionsTable: React.FC<TransactionsTableProps> = ({
  transactions,
  accounts,
  onAddTransaction,
  onTransfer,
  onDeleteTransaction,
  isAddModalOpen,
  setIsAddModalOpen,
  isTransferModalOpen,
  setIsTransferModalOpen,
}) => {
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedAccount, setSelectedAccount] = useState<string>("all");

  // Form states for Add Transaction
  const [amount, setAmount] = useState("");
  const [txnType, setTxnType] = useState<"income" | "expense">("expense");
  const [category, setCategory] = useState("Groceries");
  const [accountId, setAccountId] = useState(accounts[0]?.id || "");
  const [dateStr, setDateStr] = useState(new Date().toISOString().split("T")[0]);
  const [description, setDescription] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("Debit Card");
  const [recurring, setRecurring] = useState("none");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Form states for Transfer
  const [fromAccountId, setFromAccountId] = useState(accounts[0]?.id || "");
  const [toAccountId, setToAccountId] = useState(accounts[1]?.id || "");
  const [transferAmount, setTransferAmount] = useState("");
  const [transferDate, setTransferDate] = useState(new Date().toISOString().split("T")[0]);
  const [transferDesc, setTransferDesc] = useState("Inter-account savings transfer");
  const [transferError, setTransferError] = useState<string | null>(null);

  const categories = useMemo(() => {
    const set = new Set<string>();
    transactions.forEach((t) => {
      if (t.category) set.add(t.category);
    });
    return Array.from(set).sort();
  }, [transactions]);

  const filteredTransactions = useMemo(() => {
    return transactions.filter((t) => {
      const matchSearch =
        search === "" ||
        (t.description || "").toLowerCase().includes(search.toLowerCase()) ||
        t.category.toLowerCase().includes(search.toLowerCase()) ||
        t.amount.includes(search);

      const matchType = selectedType === "all" || t.type === selectedType;
      const matchCategory = selectedCategory === "all" || t.category === selectedCategory;
      const matchAccount =
        selectedAccount === "all" ||
        t.account_id === selectedAccount ||
        t.target_account_id === selectedAccount;

      return matchSearch && matchType && matchCategory && matchAccount;
    });
  }, [transactions, search, selectedType, selectedCategory, selectedAccount]);

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!amount || parseFloat(amount) <= 0) {
      setFormError("Amount must be greater than zero.");
      return;
    }
    setFormError(null);
    setIsSubmitting(true);
    try {
      await onAddTransaction({
        amount: parseFloat(amount).toFixed(2),
        type: txnType,
        category,
        account_id: accountId,
        date: dateStr,
        description: description.trim(),
        payment_method: paymentMethod,
        recurring,
      });
      setIsAddModalOpen(false);
      setAmount("");
      setDescription("");
    } catch (err: any) {
      setFormError(err.message || "Failed to record transaction.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTransferSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!transferAmount || parseFloat(transferAmount) <= 0) {
      setTransferError("Amount must be greater than zero.");
      return;
    }
    if (fromAccountId === toAccountId) {
      setTransferError("Source and destination accounts must be different.");
      return;
    }
    setTransferError(null);
    setIsSubmitting(true);
    try {
      await onTransfer({
        from_account_id: fromAccountId,
        to_account_id: toAccountId,
        amount: parseFloat(transferAmount).toFixed(2),
        date: transferDate,
        description: transferDesc.trim(),
      });
      setIsTransferModalOpen(false);
      setTransferAmount("");
    } catch (err: any) {
      setTransferError(err.message || "Transfer failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatCurrency = (val: string | number) => {
    const num = typeof val === "string" ? parseFloat(val) : val;
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(num || 0);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900">
            Transaction Ledger
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Showing {filteredTransactions.length} of {transactions.length} reconciled records
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              id="input-search-transactions"
              type="text"
              placeholder="Search description, category..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-slate-900 w-52"
            />
          </div>

          {/* Type Filter */}
          <select
            id="filter-txn-type"
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-slate-900 bg-white"
          >
            <option value="all">All Types</option>
            <option value="income">Income (+)</option>
            <option value="expense">Expense (-)</option>
            <option value="transfer">Transfer (⇄)</option>
          </select>

          {/* Category Filter */}
          <select
            id="filter-txn-category"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-2.5 py-1.5 text-xs border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-slate-900 bg-white"
          >
            <option value="all">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Ledger Table */}
      <div className="overflow-x-auto rounded-lg border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-xs">
          <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider text-[11px]">
            <tr>
              <th className="px-4 py-3 text-left">Date</th>
              <th className="px-4 py-3 text-left">Type</th>
              <th className="px-4 py-3 text-left">Category</th>
              <th className="px-4 py-3 text-left">Description</th>
              <th className="px-4 py-3 text-left">Account</th>
              <th className="px-4 py-3 text-right">Amount</th>
              <th className="px-4 py-3 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-100">
            {filteredTransactions.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-400">
                  No transactions match the selected filters.
                </td>
              </tr>
            ) : (
              filteredTransactions.map((t) => {
                let badgeClass = "bg-slate-100 text-slate-700";
                let sign = "";
                let amountClass = "text-slate-900 font-semibold";

                if (t.type === "income") {
                  badgeClass = "bg-emerald-50 text-emerald-700 border border-emerald-200";
                  sign = "+";
                  amountClass = "text-emerald-700 font-bold";
                } else if (t.type === "expense") {
                  badgeClass = "bg-rose-50 text-rose-700 border border-rose-200";
                  sign = "-";
                  amountClass = "text-rose-600 font-bold";
                } else if (t.type === "transfer") {
                  badgeClass = "bg-indigo-50 text-indigo-700 border border-indigo-200";
                  sign = "⇄ ";
                  amountClass = "text-indigo-700 font-bold";
                }

                return (
                  <tr
                    key={t.id}
                    id={`txn-row-${t.id}`}
                    className="hover:bg-slate-50/80 transition-colors"
                  >
                    <td className="px-4 py-3 font-mono text-slate-600 whitespace-nowrap">
                      {t.date}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${badgeClass}`}>
                        {t.type}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-900 whitespace-nowrap">
                      {t.category}
                    </td>
                    <td className="px-4 py-3 text-slate-600 max-w-xs truncate" title={t.description}>
                      {t.description || "—"}
                    </td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                      {t.account_name || t.account_id}
                      {t.target_account_name && (
                        <span className="text-slate-400"> → {t.target_account_name}</span>
                      )}
                    </td>
                    <td className={`px-4 py-3 text-right whitespace-nowrap ${amountClass}`}>
                      {sign}
                      {formatCurrency(t.amount)}
                    </td>
                    <td className="px-4 py-3 text-center whitespace-nowrap">
                      <button
                        id={`btn-delete-txn-${t.id}`}
                        onClick={() => onDeleteTransaction(t.id)}
                        className="text-slate-400 hover:text-rose-600 p-1 rounded-md transition-colors"
                        title="Delete transaction and reconcile balance"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Add Transaction Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">
              Add New Transaction
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Record a financial transaction into the ACID-compliant SQLite ledger.
            </p>

            {formError && (
              <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
                {formError}
              </div>
            )}

            <form onSubmit={handleAddSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Transaction Type
                  </label>
                  <select
                    id="select-txn-type"
                    value={txnType}
                    onChange={(e) => setTxnType(e.target.value as any)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                  >
                    <option value="expense">Expense (-)</option>
                    <option value="income">Income (+)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Amount ($)
                  </label>
                  <input
                    id="input-txn-amount"
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="0.00"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Category
                  </label>
                  <input
                    id="input-txn-category"
                    type="text"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    placeholder="Groceries, Rent, Salary..."
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Account
                  </label>
                  <select
                    id="select-txn-account"
                    value={accountId}
                    onChange={(e) => setAccountId(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                  >
                    {accounts.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.name} ({formatCurrency(a.balance)})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Date
                  </label>
                  <input
                    id="input-txn-date"
                    type="date"
                    value={dateStr}
                    onChange={(e) => setDateStr(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Payment Method
                  </label>
                  <select
                    id="select-payment-method"
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                  >
                    <option value="Debit Card">Debit Card</option>
                    <option value="Credit Card">Credit Card</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                    <option value="Cash">Cash</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Description
                </label>
                <input
                  id="input-txn-desc"
                  type="text"
                  placeholder="e.g. Trader Joe's groceries"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  id="btn-submit-add-txn"
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? "Recording..." : "Record Transaction"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Transfer Funds Modal */}
      {isTransferModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <div className="flex items-center space-x-2 mb-1">
              <ArrowLeftRight className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-bold text-slate-900">
                Inter-Account Transfer
              </h3>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Atomically moves money between accounts without altering net personal wealth.
            </p>

            {transferError && (
              <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
                {transferError}
              </div>
            )}

            <form onSubmit={handleTransferSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Source Account (Debit)
                </label>
                <select
                  id="select-transfer-from"
                  value={fromAccountId}
                  onChange={(e) => setFromAccountId(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                >
                  {accounts.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({formatCurrency(a.balance)})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Destination Account (Credit)
                </label>
                <select
                  id="select-transfer-to"
                  value={toAccountId}
                  onChange={(e) => setToAccountId(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                >
                  {accounts.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({formatCurrency(a.balance)})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Transfer Amount ($)
                  </label>
                  <input
                    id="input-transfer-amount"
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="0.00"
                    value={transferAmount}
                    onChange={(e) => setTransferAmount(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Transfer Date
                  </label>
                  <input
                    id="input-transfer-date"
                    type="date"
                    value={transferDate}
                    onChange={(e) => setTransferDate(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Transfer Note
                </label>
                <input
                  id="input-transfer-note"
                  type="text"
                  value={transferDesc}
                  onChange={(e) => setTransferDesc(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsTransferModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  id="btn-submit-transfer"
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? "Transferring..." : "Execute Transfer"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

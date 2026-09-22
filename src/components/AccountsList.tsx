import React, { useState } from "react";
import {
  CreditCard,
  Building,
  Coins,
  TrendingUp,
  Plus,
  Shield,
  Percent,
} from "lucide-react";
import { AccountData } from "../types";

interface AccountsListProps {
  accounts: AccountData[];
  onAddAccount: (account: {
    name: string;
    type: string;
    initial_balance: string;
    currency: string;
    allow_overdraft: boolean;
  }) => Promise<void>;
}

export const AccountsList: React.FC<AccountsListProps> = ({
  accounts,
  onAddAccount,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [type, setType] = useState("checking");
  const [initialBalance, setInitialBalance] = useState("0.00");
  const [allowOverdraft, setAllowOverdraft] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getAccountIcon = (accType: string) => {
    switch (accType) {
      case "checking":
        return <CreditCard className="w-5 h-5 text-blue-600" />;
      case "savings":
        return <Building className="w-5 h-5 text-emerald-600" />;
      case "investment":
        return <TrendingUp className="w-5 h-5 text-purple-600" />;
      case "cash":
        return <Coins className="w-5 h-5 text-amber-600" />;
      default:
        return <CreditCard className="w-5 h-5 text-slate-600" />;
    }
  };

  const getAccountBadge = (accType: string) => {
    switch (accType) {
      case "checking":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "savings":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "investment":
        return "bg-purple-50 text-purple-700 border-purple-200";
      case "cash":
        return "bg-amber-50 text-amber-700 border-amber-200";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Account name is required.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await onAddAccount({
        name: name.trim(),
        type,
        initial_balance: initialBalance,
        currency: "USD",
        allow_overdraft: allowOverdraft,
      });
      setIsModalOpen(false);
      setName("");
      setInitialBalance("0.00");
      setAllowOverdraft(false);
    } catch (err: any) {
      setError(err.message || "Failed to create account.");
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
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-4">
        <div>
          <h2 className="text-base font-semibold text-slate-900">
            Managed Financial Accounts
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Polymorphic account classes with individual reconciliation rules
          </p>
        </div>
        <button
          id="btn-open-add-account"
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors shadow-2xs"
        >
          <Plus className="w-3.5 h-3.5 mr-1" />
          New Account
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {accounts.map((acc) => (
          <div
            key={acc.id}
            id={`account-card-${acc.id}`}
            className="border border-slate-200 rounded-xl p-4 hover:border-slate-300 hover:shadow-xs transition-all bg-white flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="p-2 rounded-lg bg-slate-50 border border-slate-100">
                  {getAccountIcon(acc.type)}
                </div>
                <span
                  className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${getAccountBadge(
                    acc.type
                  )}`}
                >
                  {acc.type}
                </span>
              </div>
              <h3 className="font-semibold text-slate-900 text-sm truncate" title={acc.name}>
                {acc.name}
              </h3>
              <div className="text-xl font-bold text-slate-900 mt-1 tracking-tight">
                {formatCurrency(acc.balance)}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
              {acc.type === "checking" && (
                <div className="flex items-center justify-between">
                  <span className="flex items-center">
                    <Shield className="w-3 h-3 mr-1 text-slate-400" /> Overdraft:
                  </span>
                  <span className="font-medium text-slate-700">
                    {acc.allow_overdraft ? "Protected ($500.00)" : "Disabled"}
                  </span>
                </div>
              )}
              {acc.type === "savings" && (
                <div className="flex items-center justify-between">
                  <span className="flex items-center">
                    <Percent className="w-3 h-3 mr-1 text-emerald-500" /> APY Yield:
                  </span>
                  <span className="font-semibold text-emerald-700">
                    {acc.perks?.interest_rate_apy || "4.25%"}
                  </span>
                </div>
              )}
              {acc.type === "investment" && (
                <div className="flex items-center justify-between">
                  <span>Class:</span>
                  <span className="font-medium text-purple-700">Equities & ETFs</span>
                </div>
              )}
              {acc.type === "cash" && (
                <div className="flex items-center justify-between">
                  <span>Medium:</span>
                  <span className="font-medium text-amber-700">Physical Vault</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Add Account Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">
              Add New Account
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Instantiate a domain account model with polymorphic balance rules.
            </p>

            {error && (
              <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Account Name
                </label>
                <input
                  id="input-account-name"
                  type="text"
                  placeholder="e.g. Fidelity Brokerage, Local Credit Union"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-slate-900"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Account Type
                  </label>
                  <select
                    id="select-account-type"
                    value={type}
                    onChange={(e) => setType(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-slate-900"
                  >
                    <option value="checking">Checking</option>
                    <option value="savings">Savings</option>
                    <option value="investment">Investment</option>
                    <option value="cash">Cash</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Opening Balance ($)
                  </label>
                  <input
                    id="input-opening-balance"
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    value={initialBalance}
                    onChange={(e) => setInitialBalance(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-slate-900"
                  />
                </div>
              </div>

              {type === "checking" && (
                <div className="flex items-center space-x-2 pt-1">
                  <input
                    id="check-allow-overdraft"
                    type="checkbox"
                    checked={allowOverdraft}
                    onChange={(e) => setAllowOverdraft(e.target.checked)}
                    className="rounded text-slate-900 focus:ring-slate-900 h-4 w-4"
                  />
                  <label
                    htmlFor="check-allow-overdraft"
                    className="text-xs font-medium text-slate-700"
                  >
                    Enable Overdraft Protection ($500.00 limit)
                  </label>
                </div>
              )}

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  id="btn-submit-account"
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? "Creating..." : "Create Account"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

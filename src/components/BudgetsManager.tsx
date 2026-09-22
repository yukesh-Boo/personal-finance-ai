import React, { useState } from "react";
import {
  Target,
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  Plus,
  RefreshCw,
  TrendingDown,
} from "lucide-react";
import { BudgetEvaluation } from "../types";

interface BudgetsManagerProps {
  budgets: BudgetEvaluation[];
  onSetBudget: (budget: {
    category: string;
    limit: string;
    period: string;
  }) => Promise<void>;
}

export const BudgetsManager: React.FC<BudgetsManagerProps> = ({
  budgets,
  onSetBudget,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [category, setCategory] = useState("Groceries");
  const [limit, setLimit] = useState("500.00");
  const [period, setPeriod] = useState("monthly");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const availableCategories = [
    "Groceries",
    "Dining & Restaurants",
    "Housing & Rent",
    "Utilities & Bills",
    "Transportation",
    "Subscriptions",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Travel",
    "Personal Care",
    "Miscellaneous",
  ];

  const formatCurrency = (val: string | number) => {
    const num = typeof val === "string" ? parseFloat(val) : val;
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(num || 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!category || !limit) {
      setError("Category and limit amount are required.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await onSetBudget({
        category,
        limit,
        period,
      });
      setIsModalOpen(false);
      setLimit("500.00");
    } catch (err: any) {
      setError(err.message || "Failed to update budget.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-4 gap-3">
        <div>
          <div className="flex items-center space-x-2">
            <Target className="w-5 h-5 text-indigo-600" />
            <h2 className="text-base font-semibold text-slate-900">
              Category Budgets & Overrun Guard
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Automated threshold monitoring: Healthy (&lt;80%), Warning (&ge;80%), Overrun (&gt;100%) with rollover support.
          </p>
        </div>

        <button
          id="btn-open-set-budget"
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors shadow-2xs self-start sm:self-auto"
        >
          <Plus className="w-3.5 h-3.5 mr-1" />
          Set / Adjust Budget
        </button>
      </div>

      {/* Grid of Budget Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {budgets.map((b) => {
          const utilPct = Math.min(100, Math.max(0, b.utilization_percentage));
          let statusBadge = "bg-emerald-50 text-emerald-700 border-emerald-200";
          let barColor = "bg-emerald-500";
          let icon = <CheckCircle2 className="w-4 h-4 text-emerald-600" />;

          if (b.status === "OVERRUN") {
            statusBadge = "bg-rose-50 text-rose-700 border-rose-200";
            barColor = "bg-rose-500";
            icon = <AlertCircle className="w-4 h-4 text-rose-600" />;
          } else if (b.status === "WARNING") {
            statusBadge = "bg-amber-50 text-amber-700 border-amber-200";
            barColor = "bg-amber-500";
            icon = <AlertTriangle className="w-4 h-4 text-amber-600" />;
          }

          return (
            <div
              key={b.budget_id}
              id={`budget-card-${b.category.toLowerCase().replace(/[^a-z0-9]/g, "-")}`}
              className="border border-slate-200 rounded-xl p-4 hover:border-slate-300 transition-all bg-white flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-slate-900 text-sm truncate" title={b.category}>
                    {b.category}
                  </h3>
                  <span
                    className={`inline-flex items-center space-x-1 text-[11px] font-bold px-2 py-0.5 rounded-full border ${statusBadge}`}
                  >
                    {icon}
                    <span>{b.status}</span>
                  </span>
                </div>

                <div className="flex items-baseline justify-between mt-2">
                  <span className="text-xl font-bold text-slate-900">
                    {formatCurrency(b.actual_spent)}
                  </span>
                  <span className="text-xs text-slate-500 font-medium">
                    of {formatCurrency(b.effective_limit)}
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-100 rounded-full h-2.5 mt-3 overflow-hidden">
                  <div
                    className={`h-2.5 rounded-full transition-all ${barColor}`}
                    style={{ width: `${utilPct}%` }}
                  />
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span>
                  {b.is_overrun ? (
                    <span className="text-rose-600 font-semibold">
                      +{formatCurrency(b.overrun_amount)} Overrun
                    </span>
                  ) : (
                    <span>{formatCurrency(b.remaining)} remaining</span>
                  )}
                </span>
                <span className="font-medium text-slate-700">
                  {b.utilization_percentage.toFixed(1)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Set Budget Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">
              Configure Spending Budget
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Set monthly expenditure ceilings with warning thresholds and rollover support.
            </p>

            {error && (
              <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Category
                </label>
                <select
                  id="select-budget-category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-slate-900"
                >
                  {availableCategories.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Spending Limit ($)
                  </label>
                  <input
                    id="input-budget-limit"
                    type="number"
                    step="1"
                    min="1"
                    value={limit}
                    onChange={(e) => setLimit(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-slate-900"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Period
                  </label>
                  <select
                    id="select-budget-period"
                    value={period}
                    onChange={(e) => setPeriod(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-slate-900"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="weekly">Weekly</option>
                    <option value="annual">Annual</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  id="btn-submit-budget"
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-lg transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? "Saving..." : "Save Budget"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

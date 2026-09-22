import React from "react";
import {
  PieChart,
  BarChart3,
  Calendar,
  Sparkles,
  AlertTriangle,
  Repeat,
  ArrowUpRight,
  ArrowDownRight,
  Info,
} from "lucide-react";
import { FinancialDossier } from "../types";

interface AnalyticsPanelProps {
  dossier: FinancialDossier;
}

export const AnalyticsPanel: React.FC<AnalyticsPanelProps> = ({ dossier }) => {
  const {
    category_breakdown,
    monthly_trends,
    forecast,
    anomalous_outliers,
    subscriptions,
  } = dossier;

  const formatCurrency = (val: string | number) => {
    const num = typeof val === "string" ? parseFloat(val) : val;
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(num || 0);
  };

  return (
    <div className="space-y-6">
      {/* Predictive Spending Forecast & Subscriptions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Next Month Predictive Forecast Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-indigo-600" />
                <h2 className="text-base font-semibold text-slate-900">
                  Spending Forecast ({forecast.forecast_month})
                </h2>
              </div>
              <span className="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                Exponential Smoothing (α=0.5)
              </span>
            </div>

            {forecast.has_sufficient_data ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                    <span className="text-xs font-semibold uppercase text-slate-500">
                      Projected Expenses
                    </span>
                    <div className="text-2xl font-bold text-slate-900 mt-1">
                      {formatCurrency(forecast.estimated_expenses)}
                    </div>
                    <span className="text-[11px] text-slate-500 mt-0.5 block">
                      Range: {formatCurrency(forecast.expenses_lower_bound)} - {formatCurrency(forecast.expenses_upper_bound)}
                    </span>
                  </div>

                  <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200">
                    <span className="text-xs font-semibold uppercase text-emerald-800">
                      Projected Net Savings
                    </span>
                    <div className="text-2xl font-bold text-emerald-700 mt-1">
                      +{formatCurrency(forecast.projected_net_savings)}
                    </div>
                    <span className="text-[11px] text-emerald-700 font-medium mt-0.5 block">
                      Expected {forecast.projected_savings_rate_pct}% savings rate
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-500 leading-relaxed">
                  Mathematical weighted estimation computed across recent multi-month trendlines, dampening random fluctuations while preserving seasonal cadence.
                </p>
              </div>
            ) : (
              <div className="p-6 text-center text-slate-400 text-xs">
                Additional monthly history required to establish statistical confidence intervals.
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-start space-x-2 text-[11px] text-slate-400">
            <Info className="w-3.5 h-3.5 shrink-0 mt-0.5 text-slate-400" />
            <span>{forecast.disclaimer}</span>
          </div>
        </div>

        {/* Detected Recurring Subscriptions Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <Repeat className="w-5 h-5 text-purple-600" />
                <h2 className="text-base font-semibold text-slate-900">
                  Recurring Charges & Subscriptions
                </h2>
              </div>
              <span className="text-xs font-bold text-slate-500">
                {subscriptions.length} active cadences
              </span>
            </div>

            <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
              {subscriptions.length === 0 ? (
                <div className="text-center py-6 text-slate-400 text-xs">
                  No repeating recurring charges detected in ledger.
                </div>
              ) : (
                subscriptions.map((sub, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition-colors"
                  >
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 truncate max-w-xs">
                        {sub.name}
                      </h4>
                      <p className="text-[11px] text-slate-500">
                        {sub.category} • {sub.cadence} • Last: {sub.last_billed}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-bold text-slate-900">
                        {formatCurrency(sub.typical_amount)} / mo
                      </span>
                      <span className="block text-[10px] text-slate-400 font-mono">
                        ≈ {formatCurrency(sub.estimated_annual_cost)} / yr
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-400">
            Detected automatically via transaction recurrence and uniform pricing patterns.
          </div>
        </div>
      </div>

      {/* Category Breakdown & Monthly Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Spending Breakdown */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
            <div className="flex items-center space-x-2">
              <PieChart className="w-5 h-5 text-emerald-600" />
              <h2 className="text-base font-semibold text-slate-900">
                Spending by Category
              </h2>
            </div>
            <span className="text-xs text-slate-500">
              Total Breakdown
            </span>
          </div>

          <div className="space-y-4">
            {category_breakdown.map((cat, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-semibold text-slate-800">
                    {cat.category}
                  </span>
                  <div className="space-x-2">
                    <span className="font-bold text-slate-900">
                      {formatCurrency(cat.amount)}
                    </span>
                    <span className="text-slate-400 font-medium">
                      ({cat.percentage.toFixed(1)}%)
                    </span>
                  </div>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div
                    className="bg-slate-800 h-2 rounded-full"
                    style={{ width: `${Math.min(100, cat.percentage)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly Financial Trends */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <h2 className="text-base font-semibold text-slate-900">
                Historical Monthly Trends
              </h2>
            </div>
            <span className="text-xs text-slate-500">
              MoM Growth Analysis
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold uppercase text-[10px]">
                <tr>
                  <th className="px-3 py-2 text-left">Month</th>
                  <th className="px-3 py-2 text-right">Income</th>
                  <th className="px-3 py-2 text-right">Expenses</th>
                  <th className="px-3 py-2 text-right">MoM %</th>
                  <th className="px-3 py-2 text-right">Savings Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {monthly_trends.map((m, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60">
                    <td className="px-3 py-2.5 font-mono font-medium text-slate-900">
                      {m.month}
                    </td>
                    <td className="px-3 py-2.5 text-right font-medium text-emerald-700">
                      +{formatCurrency(m.income)}
                    </td>
                    <td className="px-3 py-2.5 text-right font-medium text-rose-600">
                      -{formatCurrency(m.expense)}
                    </td>
                    <td className="px-3 py-2.5 text-right font-medium">
                      {m.mom_expense_growth_pct === null ? (
                        <span className="text-slate-400">—</span>
                      ) : m.mom_expense_growth_pct > 0 ? (
                        <span className="text-rose-600 inline-flex items-center">
                          +{m.mom_expense_growth_pct.toFixed(1)}%
                          <ArrowUpRight className="w-3 h-3 ml-0.5" />
                        </span>
                      ) : (
                        <span className="text-emerald-700 inline-flex items-center">
                          {m.mom_expense_growth_pct.toFixed(1)}%
                          <ArrowDownRight className="w-3 h-3 ml-0.5" />
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2.5 text-right font-bold text-indigo-700">
                      {m.savings_rate_pct.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Anomalous Outlier Spending Alerts */}
      {anomalous_outliers.length > 0 && (
        <div className="bg-amber-50/60 border border-amber-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center space-x-2 text-amber-900 font-semibold text-sm mb-3">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>Statistical Outlier Spending Detected (IQR & Modified Z-Score)</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {anomalous_outliers.map((o, idx) => (
              <div
                key={idx}
                className="bg-white border border-amber-200 rounded-lg p-3 text-xs shadow-2xs"
              >
                <div className="flex items-center justify-between mb-1 font-bold text-slate-900">
                  <span>{o.category}</span>
                  <span className="text-rose-600">{formatCurrency(o.amount)}</span>
                </div>
                <p className="text-slate-600 text-[11px] mb-1">
                  {o.anomaly_reason}
                </p>
                <span className="text-[10px] text-slate-400 font-mono">
                  Recorded on {o.date} • {o.description || "Unspecified"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

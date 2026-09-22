import React from "react";
import {
  TrendingUp,
  TrendingDown,
  PiggyBank,
  Percent,
  ShieldCheck,
  AlertTriangle,
  ArrowUpRight,
  Info,
} from "lucide-react";
import { FinancialDossier } from "../types";

interface MetricsOverviewProps {
  dossier: FinancialDossier;
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({ dossier }) => {
  const { summary, accounts, financial_health, spending_velocity } = dossier;

  // Calculate total liquid wealth from accounts
  const totalLiquidWealth = accounts.reduce(
    (acc, cur) => acc + parseFloat(cur.balance || "0"),
    0
  );

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
      {/* Top 4 KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Liquid Wealth */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">
              Total Liquid Wealth
            </span>
            <PiggyBank className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900 tracking-tight">
            {formatCurrency(totalLiquidWealth)}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Across {accounts.length} active accounts (Checking, Savings, Cash)
          </p>
        </div>

        {/* Total Income */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">
              Total Incomes
            </span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-700 tracking-tight">
            +{formatCurrency(summary.total_income)}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Salaries, dividends & consulting revenues
          </p>
        </div>

        {/* Total Expenses */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">
              Total Expenses
            </span>
            <TrendingDown className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold text-rose-600 tracking-tight">
            -{formatCurrency(summary.total_expenses)}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {summary.transaction_count} recorded transactions
          </p>
        </div>

        {/* Savings Rate & Net Savings */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">
              Savings Rate
            </span>
            <Percent className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold text-indigo-700 tracking-tight">
              {summary.savings_rate_pct.toFixed(1)}%
            </span>
            <span className="text-xs font-semibold text-slate-500">
              ({formatCurrency(summary.net_savings)} net)
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Exceeds 20% healthy threshold
          </p>
        </div>
      </div>

      {/* Financial Health Scorecard & Spending Velocity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Health Scorecard Card (2 cols) */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                <h2 className="text-base font-semibold text-slate-900">
                  Financial Health & Stability Index
                </h2>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                {financial_health.rating}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-center">
              {/* Score circle */}
              <div className="sm:col-span-1 flex flex-col items-center justify-center p-4 bg-slate-50 rounded-xl border border-slate-200 text-center">
                <span className="text-4xl font-extrabold text-slate-900 tracking-tight">
                  {financial_health.score}
                </span>
                <span className="text-xs uppercase font-bold text-slate-400 mt-1">
                  Out of 100
                </span>
              </div>

              {/* Component breakdown */}
              <div className="sm:col-span-3 space-y-3">
                {/* Savings Rate score */}
                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                    <span>Savings Rate Factor</span>
                    <span className="text-slate-500 font-semibold">
                      {financial_health.component_breakdown.savings_rate_score.points} / {financial_health.component_breakdown.savings_rate_score.max} pts
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className="bg-emerald-500 h-2 rounded-full"
                      style={{
                        width: `${(financial_health.component_breakdown.savings_rate_score.points / financial_health.component_breakdown.savings_rate_score.max) * 100}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Budget Discipline score */}
                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                    <span>Budget Discipline</span>
                    <span className="text-slate-500 font-semibold">
                      {financial_health.component_breakdown.budget_discipline_score.points} / {financial_health.component_breakdown.budget_discipline_score.max} pts
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className="bg-indigo-500 h-2 rounded-full"
                      style={{
                        width: `${(financial_health.component_breakdown.budget_discipline_score.points / financial_health.component_breakdown.budget_discipline_score.max) * 100}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Emergency Buffer score */}
                <div>
                  <div className="flex justify-between text-xs font-medium text-slate-700 mb-1">
                    <span>Liquidity & Emergency Buffer</span>
                    <span className="text-slate-500 font-semibold">
                      {financial_health.component_breakdown.liquidity_buffer_score.points} / {financial_health.component_breakdown.liquidity_buffer_score.max} pts
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{
                        width: `${(financial_health.component_breakdown.liquidity_buffer_score.points / financial_health.component_breakdown.liquidity_buffer_score.max) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600 flex items-center">
            <Info className="w-4 h-4 mr-1.5 text-slate-400 shrink-0" />
            <span>{financial_health.guidance}</span>
          </div>
        </div>

        {/* Spending Velocity Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <h2 className="text-base font-semibold text-slate-900">
                Spending Velocity
              </h2>
              <span className="text-xs text-slate-400">
                {spending_velocity.window_days}-day window
              </span>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between py-1 border-b border-slate-50">
                <span className="text-xs text-slate-500 font-medium">
                  Average Daily Spend
                </span>
                <span className="text-sm font-bold text-slate-900">
                  {formatCurrency(spending_velocity.average_daily_spend)} / day
                </span>
              </div>

              <div className="flex items-center justify-between py-1 border-b border-slate-50">
                <span className="text-xs text-slate-500 font-medium">
                  Average Weekly Run-rate
                </span>
                <span className="text-sm font-bold text-slate-900">
                  {formatCurrency(spending_velocity.average_weekly_spend)} / wk
                </span>
              </div>

              <div className="flex items-center justify-between py-1">
                <span className="text-xs text-slate-500 font-medium">
                  Projected Monthly Burn
                </span>
                <span className="text-sm font-bold text-indigo-600">
                  {formatCurrency(spending_velocity.projected_monthly_spend)} / mo
                </span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-400">
            Computed dynamically from 30-day trailing settled transactions.
          </div>
        </div>
      </div>
    </div>
  );
};

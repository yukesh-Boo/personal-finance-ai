export interface AccountPerks {
  overdraft_protected?: boolean;
  overdraft_limit?: string;
  interest_rate_apy?: string;
  yield_type?: string;
  asset_class?: string;
  capital_gains_tracking?: boolean;
  physical_currency?: boolean;
  [key: string]: any;
}

export interface AccountData {
  id: string;
  name: string;
  type: "checking" | "savings" | "cash" | "investment";
  initial_balance: string;
  balance: string;
  currency: string;
  allow_overdraft: boolean;
  perks: AccountPerks;
}

export interface TransactionData {
  id: string;
  amount: string;
  type: "income" | "expense" | "transfer";
  category: string;
  account_id: string;
  account_name?: string;
  target_account_id?: string | null;
  target_account_name?: string | null;
  date: string;
  description: string;
  payment_method: string;
  recurring: string;
  is_verified?: boolean;
}

export interface CategoryBreakdown {
  category: string;
  amount: string;
  percentage: number;
  count: number;
}

export interface MonthlyTrend {
  month: string;
  income: string;
  expense: string;
  net_savings: string;
  savings_rate_pct: number;
  mom_expense_growth_pct: number | null;
}

export interface SpendingVelocity {
  window_days: number;
  total_spent_window: string;
  average_daily_spend: string;
  average_weekly_spend: string;
  projected_monthly_spend: string;
}

export interface AnomalyOutlier {
  transaction_id: string;
  date: string;
  category: string;
  description: string;
  amount: string;
  category_average: string;
  z_score: number;
  multiplier_of_avg: number;
  anomaly_reason: string;
}

export interface SubscriptionItem {
  name: string;
  category: string;
  typical_amount: string;
  cadence: string;
  occurrence_count: number;
  last_billed: string;
  estimated_annual_cost: string;
}

export interface SpendingForecast {
  has_sufficient_data: boolean;
  methodology: string;
  forecast_month: string;
  estimated_expenses: string;
  expenses_lower_bound: string;
  expenses_upper_bound: string;
  projected_income: string;
  projected_net_savings: string;
  projected_savings_rate_pct: number;
  disclaimer: string;
}

export interface BudgetEvaluation {
  budget_id: string;
  category: string;
  base_limit: string;
  rollover_amount: string;
  effective_limit: string;
  actual_spent: string;
  remaining: string;
  utilization_percentage: number;
  is_warning_80: boolean;
  is_overrun: boolean;
  overrun_amount: string;
  status: "HEALTHY" | "WARNING" | "OVERRUN";
}

export interface HealthScoreComponent {
  points: number;
  max: number;
  detail: string;
}

export interface FinancialHealthScore {
  score: number;
  rating: string;
  guidance: string;
  component_breakdown: {
    savings_rate_score: HealthScoreComponent;
    budget_discipline_score: HealthScoreComponent;
    liquidity_buffer_score: HealthScoreComponent;
    stability_score: HealthScoreComponent;
  };
}

export interface FinancialDossier {
  summary: {
    total_income: string;
    total_expenses: string;
    net_savings: string;
    savings_rate_pct: number;
    transaction_count: number;
  };
  accounts: AccountData[];
  category_breakdown: CategoryBreakdown[];
  monthly_trends: MonthlyTrend[];
  spending_velocity: SpendingVelocity;
  anomalous_outliers: AnomalyOutlier[];
  subscriptions: SubscriptionItem[];
  forecast: SpendingForecast;
  budget_evaluations: BudgetEvaluation[];
  financial_health: FinancialHealthScore;
}

export interface VehicleAnalysis {
  vehicleid: number;
  licenseno: string | null;
  fueltypes: string;
  total_mileage: number;
  total_fuel: number;
  total_energy_kwh: number;
  tour_count: number;
  feasible_tours: number;
  infeasible_tours: number;
  feasible_days: number;
  infeasible_days: number;
  total_days: number;
  avg_consumption_per_100km: number;
  annual_mileage: number;
  annual_energy_kwh: number;
  cost_diesel: number;
  cost_lng: number;
  cost_bev: number;
  economy_per_year: number;
  feasibility_flag: string;
  cost_efficiency_flag: string;
  both: string;
  feasible_rate: number;
}

export interface FuelSummaryRow {
  fueltypes: string;
  vehicles: number;
  feasible: number;
  cost_efficient: number;
  avg_economy: number;
  total_economy: number;
}

export interface DailyTrendPoint {
  date: string;
  tour_count: number;
  mileage_sum: number;
  fuel_sum: number;
  energy_sum: number;
  feasible_rate: number;
}

export interface EconomyHighlight {
  vehicleid: number;
  licenseno: string | null;
  fueltypes: string;
  economy_per_year: number;
  cost_bev: number;
}

export interface AISummary {
  headline: string;
  bullets: string[];
  cautions?: string[];
  raw?: string;
}

export interface AnalysisResponse {
  energy_limit_kwh: number;
  period_months: number;
  start_date: string;
  end_date: string;
  total_vehicles: number;
  total_tours: number;
  total_mileage: number;
  total_energy_kwh: number;
  vehicles: VehicleAnalysis[];
  fuel_summary: FuelSummaryRow[];
  feasibility_breakdown: Record<string, number>;
  cost_efficiency_breakdown: Record<string, number>;
  both_yes_count: number;
  economy_extremes: {
    top_savers: EconomyHighlight[];
    top_risks: EconomyHighlight[];
  };
  daily_trend: DailyTrendPoint[];
  tco_parameters: Record<string, Record<string, number>>;
  insights: Record<string, string>;
  ai_summary?: AISummary | null;
}

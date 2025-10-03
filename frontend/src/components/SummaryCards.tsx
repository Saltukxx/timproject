interface MetricCardProps {
  label: string;
  value: string;
  accent?: "default" | "success" | "warning";
  helper?: string;
}

function MetricCard({ label, value, accent = "default", helper }: MetricCardProps) {
  const accentClass =
    accent === "success" ? "status-chip success" : accent === "warning" ? "status-chip warning" : "status-chip";

  return (
    <div className="card">
      <span className="card-title">{label}</span>
      <p className="stat-value">{value}</p>
      {helper && <span className={accentClass}>{helper}</span>}
    </div>
  );
}

interface SummaryCardsProps {
  totalVehicles: number;
  totalTours: number;
  totalMileage: number;
  totalEnergy: number;
  feasibilityCounts: Record<string, number>;
  costEfficiencyCounts: Record<string, number>;
  bothYes: number;
}

export function SummaryCards({
  totalVehicles,
  totalTours,
  totalMileage,
  totalEnergy,
  feasibilityCounts,
  costEfficiencyCounts,
  bothYes
}: SummaryCardsProps) {
  const feasibleVehicles = feasibilityCounts["yes"] ?? 0;
  const costEfficient = costEfficiencyCounts["yes"] ?? 0;
  return (
    <div className="grid metrics">
      <MetricCard
        label="Fleet Scope"
        value={`${totalVehicles.toLocaleString()} vehicles`}
        helper={`${totalTours.toLocaleString()} tours analyzed`}
      />
      <MetricCard
        label="Annualized Mileage"
        value={`${Math.round(totalMileage).toLocaleString()} km`}
        helper={`Energy: ${Math.round(totalEnergy).toLocaleString()} kWh`}
      />
      <MetricCard
        label="BEV Feasibility"
        value={`${feasibleVehicles} vehicles`}
        accent="success"
        helper={`${bothYes} fully ready`}
      />
      <MetricCard
        label="Cost Efficiency"
        value={`${costEfficient} vehicles`}
        accent="warning"
        helper={`${(costEfficiencyCounts["no"] ?? 0)} require optimisation`}
      />
    </div>
  );
}


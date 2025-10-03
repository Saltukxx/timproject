import { FileUploader } from "./components/FileUploader";
import { SummaryCards } from "./components/SummaryCards";
import { VehicleTable } from "./components/VehicleTable";
import { EconomyBarChart } from "./components/Charts/EconomyBarChart";
import { FeasibilityPieChart } from "./components/Charts/FeasibilityPieChart";
import { DailyTrendChart } from "./components/Charts/DailyTrendChart";
import { useAnalysis } from "./hooks/useAnalysis";
import { InsightPanel } from "./components/InsightPanel";

function formatRange(start: string, end: string) {
  if (!start || !end) return "";
  return `${start} → ${end}`;
}

export default function App() {
  const { data, loading, error, upload } = useAnalysis();

  return (
    <main>
      <FileUploader onFileSelected={upload} loading={loading} />
      {error && (
        <div className="card" style={{ marginTop: "1.5rem", border: "1px solid rgba(255,107,107,0.3)" }}>
          <span className="status-chip danger">{error}</span>
        </div>
      )}

      {data ? (
        <>
          <div style={{ margin: "1.5rem 0 2rem" }}>
            <span className="status-chip success">Energy limit {Math.round(data.energy_limit_kwh)} kWh</span>
            <span className="status-chip" style={{ marginLeft: "0.75rem" }}>
              Period {data.period_months} months ({formatRange(data.start_date, data.end_date)})
            </span>
          </div>

          <SummaryCards
            totalVehicles={data.total_vehicles}
            totalTours={data.total_tours}
            totalMileage={data.total_mileage}
            totalEnergy={data.total_energy_kwh}
            feasibilityCounts={data.feasibility_breakdown}
            costEfficiencyCounts={data.cost_efficiency_breakdown}
            bothYes={data.both_yes_count}
          />

          <div className="grid analysis" style={{ marginTop: "1.5rem" }}>
            <EconomyBarChart
              positives={data.economy_extremes.top_savers}
              negatives={data.economy_extremes.top_risks}
            />
            <FeasibilityPieChart
              feasibility={data.feasibility_breakdown}
              cost={data.cost_efficiency_breakdown}
              both={data.both_yes_count}
            />
          </div>

          <div style={{ marginTop: "1.5rem" }}>
            <DailyTrendChart data={data.daily_trend} />
          </div>

          <InsightPanel insights={data.insights} aiSummary={data.ai_summary ?? undefined} />

          <div style={{ marginTop: "1.5rem" }}>
            <VehicleTable vehicles={data.vehicles} />
          </div>
        </>
      ) : (
        <div className="card" style={{ marginTop: "2rem" }}>
          <h2 className="section-title">How it works</h2>
          <p className="stat-label">
            Upload the latest macro workbook straight from Qivalon. We will rebuild the feasibility pivot, execute
            the TCO stack, and highlight the strongest BEV opportunities. Use the filters once the report is in.
          </p>
        </div>
      )}
    </main>
  );
}

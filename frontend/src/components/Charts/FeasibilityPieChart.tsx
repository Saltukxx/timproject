import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { Pie } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

interface Props {
  feasibility: Record<string, number>;
  cost: Record<string, number>;
  both: number;
}

export function FeasibilityPieChart({ feasibility, cost, both }: Props) {
  const data = {
    labels: ["Feasible", "Cost Efficient", "Both"],
    datasets: [
      {
        label: "Vehicle Count",
        data: [feasibility["yes"] ?? 0, cost["yes"] ?? 0, both],
        backgroundColor: [
          "rgba(79, 140, 255, 0.75)",
          "rgba(54, 200, 138, 0.75)",
          "rgba(241, 197, 80, 0.75)"
        ],
        borderColor: "rgba(255,255,255,0.1)",
        borderWidth: 1
      }
    ]
  };

  return (
    <div className="card chart-card">
      <div className="card-header">
        <h3 className="section-title">Conversion Readiness Snapshot</h3>
      </div>
      <Pie
        data={data}
        options={{
          plugins: {
            legend: {
              position: "bottom",
              labels: {
                color: "#b4bed0"
              }
            }
          }
        }}
      />
    </div>
  );
}


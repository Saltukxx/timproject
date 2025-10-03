import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from "chart.js";
import type { EconomyHighlight } from "../../types";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

interface Props {
  positives: EconomyHighlight[];
  negatives: EconomyHighlight[];
}

export function EconomyBarChart({ positives, negatives }: Props) {
  const labels = [...negatives.map((row) => `#${row.vehicleid}`), ...positives.map((row) => `#${row.vehicleid}`)];
  const data = {
    labels,
    datasets: [
      {
        label: "Economy per year (€)",
        data: [
          ...negatives.map((row) => row.economy_per_year),
          ...positives.map((row) => row.economy_per_year)
        ],
        backgroundColor: labels.map((_, index) => (index < negatives.length ? "rgba(255, 107, 107, 0.7)" : "rgba(54, 200, 138, 0.7)")),
        borderRadius: 6
      }
    ]
  };

  return (
    <div className="card chart-card">
      <div className="card-header">
        <h3 className="section-title">Best and Worst BEV Business Cases</h3>
      </div>
      <Bar
        data={data}
        options={{
          responsive: true,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              ticks: { color: "#b4bed0" },
              grid: { color: "rgba(255,255,255,0.05)" }
            },
            y: {
              ticks: { color: "#b4bed0" },
              grid: { color: "rgba(255,255,255,0.05)" }
            }
          }
        }}
      />
    </div>
  );
}


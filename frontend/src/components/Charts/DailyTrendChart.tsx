import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from "chart.js";
import { Line } from "react-chartjs-2";
import type { DailyTrendPoint } from "../../types";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

interface Props {
  data: DailyTrendPoint[];
}

export function DailyTrendChart({ data }: Props) {
  const labels = data.map((point) => point.date);
  const chartData = {
    labels,
    datasets: [
      {
        label: "Mileage",
        data: data.map((point) => point.mileage_sum),
        borderColor: "rgba(79, 140, 255, 0.9)",
        backgroundColor: "rgba(79, 140, 255, 0.2)",
        tension: 0.35,
        fill: true,
        yAxisID: "y"
      },
      {
        label: "Tours",
        data: data.map((point) => point.tour_count),
        borderColor: "rgba(54, 200, 138, 0.9)",
        backgroundColor: "rgba(54, 200, 138, 0.15)",
        tension: 0.35,
        fill: true,
        yAxisID: "y1"
      }
    ]
  };

  return (
    <div className="card chart-card">
      <div className="card-header">
        <h3 className="section-title">Daily Volume & Activity</h3>
      </div>
      <Line
        data={chartData}
        options={{
          responsive: true,
          plugins: {
            legend: { labels: { color: "#b4bed0" } }
          },
          scales: {
            x: {
              ticks: {
                color: "#8994ab",
                maxTicksLimit: 8
              },
              grid: { color: "rgba(255,255,255,0.05)" }
            },
            y: {
              position: "left",
              ticks: { color: "#8994ab" },
              grid: { color: "rgba(255,255,255,0.05)" }
            },
            y1: {
              position: "right",
              ticks: { color: "#8994ab" },
              grid: { drawOnChartArea: false }
            }
          }
        }}
      />
    </div>
  );
}


import type { AISummary } from "../types";

interface Props {
  insights: Record<string, string>;
  aiSummary?: AISummary | null;
}

const LABELS: Record<string, string> = {
  graphs_overview: "How the charts are built",
  feasibility: "Feasibility logic",
  cost_efficiency: "Cost-efficiency logic",
  economy_chart: "Economy highlights",
  fuel_mix: "Fuel mix snapshot",
  tco_logic: "TCO methodology"
};

export function InsightPanel({ insights, aiSummary }: Props) {
  const orderedKeys = Object.keys(LABELS).filter((key) => insights[key]);

  const hasClassicInsights = orderedKeys.length > 0;
  const hasAISummary = Boolean(aiSummary);

  if (!hasClassicInsights && !hasAISummary) {
    return null;
  }

  return (
    <div className="card" style={{ marginTop: "1.5rem" }}>
      <div className="card-header">
        <h2 className="section-title">AI Insights</h2>
        <span className="stat-label">Generated from the recomputed Excel logic</span>
      </div>
      <div className="grid" style={{ gap: "1rem" }}>
        {hasAISummary && aiSummary && (
          <div style={{ background: "var(--surface-light)", borderRadius: "12px", padding: "1rem" }}>
            <strong style={{ display: "block", marginBottom: "0.5rem", color: "var(--accent)" }}>
              {aiSummary.headline}
            </strong>
            <ul style={{ margin: 0, paddingLeft: "1.2rem", color: "var(--text-primary)", lineHeight: 1.5 }}>
              {aiSummary.bullets.map((bullet, index) => (
                <li key={index}>{bullet}</li>
              ))}
            </ul>
            {aiSummary.cautions && aiSummary.cautions.length > 0 && (
              <div style={{ marginTop: "1rem" }}>
                <span className="stat-label" style={{ display: "block", marginBottom: "0.25rem" }}>
                  Cautions
                </span>
                <ul style={{ margin: 0, paddingLeft: "1.2rem", color: "var(--warning)" }}>
                  {aiSummary.cautions.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        {orderedKeys.map((key) => (
          <div key={key} style={{ background: "var(--surface-light)", borderRadius: "12px", padding: "1rem" }}>
            <strong style={{ display: "block", marginBottom: "0.5rem", color: "var(--accent)" }}>
              {LABELS[key]}
            </strong>
            <span className="stat-label" style={{ color: "var(--text-primary)", lineHeight: 1.5 }}>
              {insights[key]}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

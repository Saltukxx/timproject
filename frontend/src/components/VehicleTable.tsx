import { useMemo, useState } from "react";
import type { VehicleAnalysis } from "../types";

interface Props {
  vehicles: VehicleAnalysis[];
}

type FilterState = {
  fuel: "all" | "diesel" | "lng" | "other";
  feasibility: "all" | "yes" | "no";
  cost: "all" | "yes" | "no";
  search: string;
};

const initialFilters: FilterState = {
  fuel: "all",
  feasibility: "all",
  cost: "all",
  search: ""
};

function formatCurrency(value: number) {
  return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(
    value
  );
}

function formatNumber(value: number) {
  return new Intl.NumberFormat("de-DE", { maximumFractionDigits: 0 }).format(value);
}

export function VehicleTable({ vehicles }: Props) {
  const [filters, setFilters] = useState<FilterState>(initialFilters);

  const filtered = useMemo(() => {
    return vehicles.filter((vehicle) => {
      if (filters.fuel !== "all") {
        if (filters.fuel === "other" && ["diesel", "lng"].includes(vehicle.fueltypes)) {
          return false;
        }
        if (filters.fuel !== "other" && vehicle.fueltypes !== filters.fuel) {
          return false;
        }
      }
      if (filters.feasibility !== "all" && vehicle.feasibility_flag !== filters.feasibility) {
        return false;
      }
      if (filters.cost !== "all" && vehicle.cost_efficiency_flag !== filters.cost) {
        return false;
      }
      if (filters.search) {
        const needle = filters.search.toLowerCase();
        const haystack = `${vehicle.vehicleid}${vehicle.licenseno ?? ""}`.toLowerCase();
        if (!haystack.includes(needle)) {
          return false;
        }
      }
      return true;
    });
  }, [vehicles, filters]);

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="section-title">Vehicle-Level Outcomes</h2>
      </div>
      <div className="filters">
        <select
          value={filters.fuel}
          onChange={(event) => setFilters((prev) => ({ ...prev, fuel: event.target.value as FilterState["fuel"] }))}
        >
          <option value="all">All fuels</option>
          <option value="diesel">Diesel</option>
          <option value="lng">LNG</option>
          <option value="other">Other</option>
        </select>
        <select
          value={filters.feasibility}
          onChange={(event) =>
            setFilters((prev) => ({ ...prev, feasibility: event.target.value as FilterState["feasibility"] }))
          }
        >
          <option value="all">Feasibility: all</option>
          <option value="yes">Feasible</option>
          <option value="no">Infeasible</option>
        </select>
        <select
          value={filters.cost}
          onChange={(event) => setFilters((prev) => ({ ...prev, cost: event.target.value as FilterState["cost"] }))}
        >
          <option value="all">Economy: all</option>
          <option value="yes">Cost efficient</option>
          <option value="no">Not cost efficient</option>
        </select>
        <input
          type="search"
          placeholder="Search vehicle ID or license"
          value={filters.search}
          onChange={(event) => setFilters((prev) => ({ ...prev, search: event.target.value }))}
        />
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Vehicle</th>
              <th>Fuel</th>
              <th>Tours</th>
              <th>Annual km</th>
              <th>Feasible days</th>
              <th>Economy</th>
              <th>Cost Diesel</th>
              <th>Cost LNG</th>
              <th>Cost BEV</th>
              <th>Feasible?</th>
              <th>Cost Efficient?</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((vehicle) => (
              <tr key={vehicle.vehicleid}>
                <td>
                  <strong>{vehicle.vehicleid}</strong>
                  <div className="stat-label">{vehicle.licenseno ?? "—"}</div>
                </td>
                <td>{vehicle.fueltypes.toUpperCase()}</td>
                <td>{formatNumber(vehicle.tour_count)}</td>
                <td>{formatNumber(vehicle.annual_mileage)}</td>
                <td>
                  {vehicle.feasible_days}/{vehicle.total_days}
                  <div className="stat-label">{(vehicle.feasible_rate * 100).toFixed(1)}% tours</div>
                </td>
                <td>{formatCurrency(vehicle.economy_per_year)}</td>
                <td>{formatCurrency(vehicle.cost_diesel)}</td>
                <td>{formatCurrency(vehicle.cost_lng)}</td>
                <td>{formatCurrency(vehicle.cost_bev)}</td>
                <td>
                  <span className={`badge ${vehicle.feasibility_flag}`}>{vehicle.feasibility_flag}</span>
                </td>
                <td>
                  <span className={`badge ${vehicle.cost_efficiency_flag}`}>{vehicle.cost_efficiency_flag}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="stat-label" style={{ marginTop: "1rem" }}>
        Displaying {filtered.length.toLocaleString()} of {vehicles.length.toLocaleString()} vehicles
      </p>
    </div>
  );
}


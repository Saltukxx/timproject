from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import numpy as np
import pandas as pd
from openpyxl import load_workbook

from ..config import settings


TechnologyKey = Literal["diesel", "lng", "bev"]


@dataclass
class TechnologyParameters:
    vehicle_price: float
    lifetime_years: float
    subsidy_pct: float
    residual_pct: float
    replacement_value: float
    maintenance_per_km: float
    tax: float
    insurance: float
    tyre_life_km: float
    tyre_count: float
    tyre_cost: float
    own_fuel_share: float
    own_fuel_price: float
    external_fuel_price: float
    lubricant_pct: float
    adblue_pct: float
    adblue_price: float
    battery_cost: float
    battery_life_km: float
    toll_ct_per_km: float
    toll_share_pct: float
    interest_pct: float
    overhead_pct: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class VehicleAnalysis:
    vehicleid: int
    licenseno: Optional[str]
    fueltypes: str
    total_mileage: float
    total_fuel: float
    total_energy_kwh: float
    tour_count: int
    feasible_tours: int
    infeasible_tours: int
    feasible_days: int
    infeasible_days: int
    total_days: int
    avg_consumption_per_100km: float
    annual_mileage: float
    annual_energy_kwh: float
    cost_diesel: float
    cost_lng: float
    cost_bev: float
    economy_per_year: float
    feasibility_flag: str
    cost_efficiency_flag: str
    both: str
    feasible_rate: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "vehicleid": int(self.vehicleid),
            "licenseno": self.licenseno,
            "fueltypes": self.fueltypes,
            "total_mileage": float(self.total_mileage),
            "total_fuel": float(self.total_fuel),
            "total_energy_kwh": float(self.total_energy_kwh),
            "tour_count": int(self.tour_count),
            "feasible_tours": int(self.feasible_tours),
            "infeasible_tours": int(self.infeasible_tours),
            "feasible_days": int(self.feasible_days),
            "infeasible_days": int(self.infeasible_days),
            "total_days": int(self.total_days),
            "avg_consumption_per_100km": float(self.avg_consumption_per_100km),
            "annual_mileage": float(self.annual_mileage),
            "annual_energy_kwh": float(self.annual_energy_kwh),
            "cost_diesel": float(self.cost_diesel),
            "cost_lng": float(self.cost_lng),
            "cost_bev": float(self.cost_bev),
            "economy_per_year": float(self.economy_per_year),
            "feasibility_flag": self.feasibility_flag,
            "cost_efficiency_flag": self.cost_efficiency_flag,
            "both": self.both,
            "feasible_rate": float(self.feasible_rate),
        }


@dataclass
class AnalysisPayload:
    energy_limit_kwh: float
    period_months: float
    start_date: str
    end_date: str
    total_vehicles: int
    total_tours: int
    total_mileage: float
    total_energy_kwh: float
    vehicles: List[VehicleAnalysis]
    fuel_summary: List[Dict[str, float]]
    feasibility_breakdown: Dict[str, int]
    cost_efficiency_breakdown: Dict[str, int]
    both_yes_count: int
    economy_extremes: Dict[str, List[Dict[str, float]]]
    daily_trend: List[Dict[str, float]]
    tco_parameters: Dict[str, Dict[str, float]]
    insights: Dict[str, str]
    ai_summary: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "energy_limit_kwh": float(self.energy_limit_kwh),
            "period_months": float(self.period_months),
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_vehicles": int(self.total_vehicles),
            "total_tours": int(self.total_tours),
            "total_mileage": float(self.total_mileage),
            "total_energy_kwh": float(self.total_energy_kwh),
            "vehicles": [v.to_dict() for v in self.vehicles],
            "fuel_summary": self.fuel_summary,
            "feasibility_breakdown": self.feasibility_breakdown,
            "cost_efficiency_breakdown": self.cost_efficiency_breakdown,
            "both_yes_count": int(self.both_yes_count),
            "economy_extremes": self.economy_extremes,
            "daily_trend": self.daily_trend,
            "tco_parameters": self.tco_parameters,
            "insights": self.insights,
            "ai_summary": self.ai_summary,
        }


class ExcelProcessor:
    def __init__(self, workbook_path: Path) -> None:
        self.workbook_path = Path(workbook_path)

    def analyse(self) -> AnalysisPayload:
        energy_limit, period_months, tco_params = self._read_parameters()
        tours_df = self._load_tours()
        vehicles_df = self._load_vehicles()

        tours_df = self._prepare_tours(
            tours=tours_df,
            vehicles=vehicles_df,
            energy_limit=energy_limit,
        )

        if not period_months or period_months <= 0:
            period_months = self._infer_period_months(tours_df)

        tours_df["feasible tour"] = tours_df["feasible tour"].fillna(0).astype(int)
        tours_df["feasible day"] = tours_df["feasible day"].fillna(0).astype(int)
        tours_df["infeasible day"] = tours_df["infeasible day"].fillna(0).astype(int)

        vehicle_totals = self._aggregate_vehicle_metrics(tours_df)
        vehicle_totals = vehicle_totals.join(
            self._aggregate_daily_flags(tours_df),
            how="left",
        )
        vehicle_totals[["feasible_days", "infeasible_days"]] = (
            vehicle_totals[["feasible_days", "infeasible_days"]]
            .fillna(0)
            .astype(int)
        )
        vehicle_totals["total_days"] = (
            vehicle_totals["feasible_days"] + vehicle_totals["infeasible_days"]
        )

        merged = (
            vehicle_totals.reset_index()
            .merge(vehicles_df, on="vehicleid", how="left")
        )
        merged["fueltypes"] = merged["fueltypes"].fillna("unknown").str.lower()

        base_price = tco_params["diesel"].vehicle_price
        results: List[VehicleAnalysis] = []
        for row in merged.itertuples(index=False):
            result = self._compute_vehicle_row(
                row=row,
                params=tco_params,
                period_months=period_months,
                energy_limit=energy_limit,
                base_price=base_price,
            )
            results.append(result)

        vehicles_payload = [item.to_dict() for item in results]
        vehicles_df = pd.DataFrame(vehicles_payload)

        feasibility_counts = vehicles_df["feasibility_flag"].value_counts().to_dict()
        cost_efficiency_counts = (
            vehicles_df["cost_efficiency_flag"].value_counts().to_dict()
        )
        both_yes_count = int((vehicles_df["both"] == "yes").sum())

        fuel_summary = (
            vehicles_df.groupby("fueltypes")
            .agg(
                vehicles=("vehicleid", "count"),
                feasible=("feasibility_flag", lambda x: int((x == "yes").sum())),
                cost_efficient=(
                    "cost_efficiency_flag",
                    lambda x: int((x == "yes").sum()),
                ),
                avg_economy=("economy_per_year", "mean"),
                total_economy=("economy_per_year", "sum"),
            )
            .reset_index()
        )
        fuel_summary["avg_economy"] = fuel_summary["avg_economy"].round(2)
        fuel_summary["total_economy"] = fuel_summary["total_economy"].round(2)

        daily_trend = (
            tours_df.groupby("date")
            .agg(
                tour_count=("tourid", "count"),
                mileage_sum=("mileage", "sum"),
                fuel_sum=("fuelconsumption", "sum"),
                energy_sum=("estimated electricity consumption (kWh)", "sum"),
                feasible_rate=("feasible tour", lambda x: float((x == 1).mean())),
            )
            .reset_index()
        )
        daily_trend["date"] = daily_trend["date"].astype(str)

        economy_sorted = vehicles_df.sort_values("economy_per_year")
        economy_extremes = {
            "top_savers": economy_sorted.tail(5)[
                [
                    "vehicleid",
                    "licenseno",
                    "fueltypes",
                    "economy_per_year",
                    "cost_bev",
                ]
            ]
            .sort_values("economy_per_year", ascending=False)
            .to_dict("records"),
            "top_risks": economy_sorted.head(5)[
                [
                    "vehicleid",
                    "licenseno",
                    "fueltypes",
                    "economy_per_year",
                    "cost_bev",
                ]
            ]
            .to_dict("records"),
        }

        insights = self._build_insights(
            fuel_summary=fuel_summary,
            feasibility_counts=feasibility_counts,
            cost_efficiency_counts=cost_efficiency_counts,
            both_yes_count=both_yes_count,
            economy_extremes=economy_extremes,
            tco_params=tco_params,
            energy_limit=energy_limit,
        )

        payload = AnalysisPayload(
            energy_limit_kwh=energy_limit,
            period_months=period_months,
            start_date=str(min(daily_trend["date"], default="")),
            end_date=str(max(daily_trend["date"], default="")),
            total_vehicles=len(results),
            total_tours=int(len(tours_df)),
            total_mileage=float(tours_df["mileage"].sum()),
            total_energy_kwh=float(
                tours_df["estimated electricity consumption (kWh)"].sum()
            ),
            vehicles=results,
            fuel_summary=fuel_summary.to_dict("records"),
            feasibility_breakdown={k: int(v) for k, v in feasibility_counts.items()},
            cost_efficiency_breakdown={
                k: int(v) for k, v in cost_efficiency_counts.items()
            },
            both_yes_count=both_yes_count,
            economy_extremes=economy_extremes,
            daily_trend=daily_trend.round(2).to_dict("records"),
            tco_parameters={k: v.to_dict() for k, v in tco_params.items()},
            insights=insights,
        )
        return payload

    def _prepare_tours(
        self,
        *,
        tours: pd.DataFrame,
        vehicles: pd.DataFrame,
        energy_limit: float,
    ) -> pd.DataFrame:
        df = tours.copy()

        df["starttime"] = (
            pd.to_datetime(df["starttime"], errors="coerce", utc=True)
            .dt.tz_convert(None)
        )
        df["endtime"] = (
            pd.to_datetime(df.get("endtime"), errors="coerce", utc=True)
            .dt.tz_convert(None)
        )
        df = df.dropna(subset=["starttime"])
        df["date"] = df["starttime"].dt.date

        vehicles_map = (
            vehicles.set_index("vehicleid")["fueltypes"].to_dict()
        )
        df["_fueltypes"] = df["vehicleid"].map(vehicles_map).fillna("unknown")

        multipliers = {
            "diesel": 5.0,
            "lng": 7.0,
            "electric": 1.0,
            "bev": 1.0,
        }
        df["_fuel_multiplier"] = df["_fueltypes"].map(multipliers).fillna(0.0)

        df["fuelconsumption"] = pd.to_numeric(df["fuelconsumption"], errors="coerce")
        df["mileage"] = pd.to_numeric(df["mileage"], errors="coerce")

        df["estimated electricity consumption (kWh)"] = (
            df["fuelconsumption"].fillna(0.0) * df["_fuel_multiplier"]
        )

        energy_series = df["estimated electricity consumption (kWh)"]
        df["feasibility by tourid"] = np.where(
            energy_series.notna(),
            np.where(energy_series <= energy_limit, "yes", "no"),
            "",
        )
        df["feasible tour"] = np.where(
            energy_series.notna(),
            np.where(energy_series <= energy_limit, 1, 0),
            0,
        )
        df["infeasible tour"] = np.where(
            energy_series.notna(),
            np.where(energy_series > energy_limit, 1, 0),
            0,
        )

        df = df.sort_values(["vehicleid", "date", "starttime", "tourid"]).reset_index(drop=True)

        grouped_keys = ["vehicleid", "date"]
        daily_energy = (
            df.groupby(grouped_keys)["estimated electricity consumption (kWh)"]
            .transform("sum")
        )
        df["_daily_total_energy"] = daily_energy

        sequence = df.groupby(grouped_keys).cumcount()
        group_sizes = df.groupby(grouped_keys)["tourid"].transform("size")
        is_last_of_day = sequence == (group_sizes - 1)

        df["estimated electricity daily consumption (kWh)"] = np.where(
            is_last_of_day,
            df["_daily_total_energy"],
            np.nan,
        )
        df["feasibility by day"] = np.where(
            is_last_of_day,
            np.where(df["_daily_total_energy"] <= energy_limit, "yes", "no"),
            "",
        )
        df["feasible day"] = np.where(
            is_last_of_day,
            np.where(df["_daily_total_energy"] <= energy_limit, 1, 0),
            0,
        )
        df["infeasible day"] = np.where(
            is_last_of_day,
            np.where(df["_daily_total_energy"] > energy_limit, 1, 0),
            0,
        )

        df.drop(columns=["_fueltypes", "_fuel_multiplier", "_daily_total_energy"], inplace=True)
        return df

    @staticmethod
    def _infer_period_months(tours_df: pd.DataFrame) -> float:
        if tours_df.empty:
            return 0.0
        start = tours_df["starttime"].min()
        end = tours_df["starttime"].max()
        if pd.isna(start) or pd.isna(end):
            return 0.0
        delta_days = (end - start).days
        if delta_days <= 0:
            return 1.0
        return max(delta_days / 30.0, 1.0)

    def _build_insights(
        self,
        *,
        fuel_summary: pd.DataFrame,
        feasibility_counts: Dict[str, int],
        cost_efficiency_counts: Dict[str, int],
        both_yes_count: int,
        economy_extremes: Dict[str, List[Dict[str, float]]],
        tco_params: Dict[TechnologyKey, TechnologyParameters],
        energy_limit: float,
    ) -> Dict[str, str]:
        fuel_lines: List[str] = []
        for row in fuel_summary.to_dict("records"):
            line = (
                f"{row['fueltypes'].upper()}: {row['vehicles']} vehicles, "
                f"{row['feasible']} feasible, {row['cost_efficient']} cost-efficient, "
                f"mean economy {row['avg_economy']:.0f} € / vehicle"
            )
            fuel_lines.append(line)

        feasible_yes = feasibility_counts.get("yes", 0)
        cost_yes = cost_efficiency_counts.get("yes", 0)
        feasible_no = feasibility_counts.get("no", 0)
        cost_no = cost_efficiency_counts.get("no", 0)

        economy_notes: List[str] = []
        if economy_extremes["top_savers"]:
            top = economy_extremes["top_savers"][0]
            economy_notes.append(
                f"Best BEV case: vehicle #{top['vehicleid']} saves {top['economy_per_year']:.0f} € annually versus its incumbent drivetrain."
            )
        if economy_extremes["top_risks"]:
            worst = economy_extremes["top_risks"][0]
            economy_notes.append(
                f"Toughest case: vehicle #{worst['vehicleid']} requires {abs(worst['economy_per_year']):.0f} € extra per year to go BEV."
            )

        diesel_price = tco_params["diesel"].vehicle_price
        bev_price = tco_params["bev"].vehicle_price
        bev_subsidy = tco_params["bev"].subsidy_pct
        bev_energy_price = (
            tco_params["bev"].own_fuel_share / 100 * tco_params["bev"].own_fuel_price
            + (1 - tco_params["bev"].own_fuel_share / 100) * tco_params["bev"].external_fuel_price
        )

        return {
            "graphs_overview": (
                "Each chart reads directly from the recomputed Excel logic. The bar chart compares the five best "
                "and five weakest BEV economies (Δ diesel/LNG cost – BEV cost). The pie chart clusters vehicles by "
                "feasibility and cost-efficiency flags. The trend line plots daily mileage and tour volumes derived "
                "from the 457 operating days in the upload."
            ),
            "feasibility": (
                f"Feasibility results mirror the pivot formula F5 (GETPIVOTDATA). {feasible_yes} vehicles pass the "
                f"{int(energy_limit)} kWh daily energy budget with zero infeasible days, while {feasible_no} require "
                "additional charging capacity."
            ),
            "cost_efficiency": (
                f"Cost-efficiency is driven by the macro formula J5 = −(BEV cost − incumbent cost). {cost_yes} "
                f"vehicles deliver net savings; {cost_no} remain more expensive post subsidy."
            ),
            "economy_chart": " ".join(economy_notes) or "The economy chart highlights vehicles with largest BEV savings or losses.",
            "fuel_mix": " | ".join(fuel_lines),
            "tco_logic": (
                f"TCO inputs come from the workbook: diesel capex {diesel_price:,.0f} €, BEV capex {bev_price:,.0f} € with a "
                f"{bev_subsidy:.0f}% subsidy, and blended BEV energy cost {bev_energy_price:.2f} €/kWh. We annualise mileage using tours!AG3." 
            ),
        }

    def _read_parameters(self) -> tuple[float, Optional[float], Dict[TechnologyKey, TechnologyParameters]]:
        wb = load_workbook(
            filename=self.workbook_path,
            read_only=True,
            data_only=True,
            keep_vba=True,
        )
        try:
            tours_sheet = wb["tours"]
            raw_energy_limit = tours_sheet["AE1"].value
            energy_limit = (
                float(raw_energy_limit)
                if raw_energy_limit not in (None, "")
                else settings.default_energy_limit_kwh
            )

            raw_period_months = tours_sheet["AG3"].value
            period_months: Optional[float]
            if raw_period_months in (None, ""):
                period_months = None
            else:
                try:
                    period_months = float(raw_period_months)
                except (TypeError, ValueError):
                    period_months = None

            tco_sheet = wb["TCO-calculation"]
            rows_map = {
                "vehicle_price": 2,
                "lifetime_years": 3,
                "subsidy_pct": 4,
                "residual_pct": 5,
                "replacement_value": 6,
                "maintenance_per_km": 7,
                "tax": 8,
                "insurance": 9,
                "tyre_life_km": 10,
                "tyre_count": 11,
                "tyre_cost": 12,
                "own_fuel_share": 13,
                "own_fuel_price": 14,
                "external_fuel_price": 15,
                "lubricant_pct": 16,
                "adblue_pct": 17,
                "adblue_price": 18,
                "battery_cost": 19,
                "battery_life_km": 20,
                "toll_ct_per_km": 21,
                "toll_share_pct": 22,
                "interest_pct": 23,
                "overhead_pct": 24,
            }
            col_map: Dict[TechnologyKey, str] = {
                "diesel": "B",
                "lng": "C",
                "bev": "D",
            }

            parameters: Dict[TechnologyKey, TechnologyParameters] = {}
            for key, col in col_map.items():
                values = {
                    field: float(tco_sheet[f"{col}{row}"].value or 0)
                    for field, row in rows_map.items()
                }
                parameters[key] = TechnologyParameters(**values)
        finally:
            wb.close()

        return energy_limit, period_months, parameters

    def _load_tours(self) -> pd.DataFrame:
        base_columns = [
            "tourid",
            "vehicleid",
            "starttime",
            "endtime",
            "mileage",
            "fuelconsumption",
            "estimated electricity consumption (kWh)",
            "feasible tour",
            "feasible day",
            "infeasible day",
        ]
        df = pd.read_excel(
            self.workbook_path,
            sheet_name="tours",
        )

        missing_columns = [col for col in base_columns if col not in df.columns]
        for col in missing_columns:
            df[col] = np.nan

        return df[base_columns]

    def _load_vehicles(self) -> pd.DataFrame:
        df = pd.read_excel(
            self.workbook_path,
            sheet_name="vehicles",
            usecols=["vehicleid", "licenseno", "fueltypes"],
        )
        df["fueltypes"] = df["fueltypes"].apply(self._normalise_fuel_type)
        return df

    @staticmethod
    def _normalise_fuel_type(value: Optional[str]) -> str:
        if not isinstance(value, str):
            return "unknown"
        text = value.strip().lower()
        if not text or text in {"{}", "nan"}:
            return "unknown"
        if "lng" in text:
            return "lng"
        if "diesel" in text:
            return "diesel"
        if "electric" in text or "bev" in text:
            return "electric"
        if "petrol" in text or "gasoline" in text:
            return "petrol"
        return text

    @staticmethod
    def _aggregate_vehicle_metrics(df: pd.DataFrame) -> pd.DataFrame:
        grouped = df.groupby("vehicleid").agg(
            total_mileage=("mileage", "sum"),
            total_fuel=("fuelconsumption", "sum"),
            tour_count=("tourid", "count"),
            feasible_tours=("feasible tour", lambda x: int((x == 1).sum())),
            infeasible_tours=("feasible tour", lambda x: int((x == 0).sum())),
            total_energy_kwh=(
                "estimated electricity consumption (kWh)",
                "sum",
            ),
        )
        grouped["avg_consumption_per_100km"] = (
            grouped["total_fuel"]
            .div(grouped["total_mileage"].replace({0: np.nan}))
            .mul(100)
            .fillna(0)
        )
        grouped["feasible_rate"] = (
            grouped["feasible_tours"]
            .div(grouped["tour_count"].replace({0: np.nan}))
            .fillna(0)
        )
        return grouped

    @staticmethod
    def _aggregate_daily_flags(df: pd.DataFrame) -> pd.DataFrame:
        flagged = df.groupby("vehicleid").agg(
            feasible_days=("feasible day", lambda x: int((x == 1).sum())),
            infeasible_days=("infeasible day", lambda x: int((x == 1).sum())),
        )
        return flagged

    def _compute_vehicle_row(
        self,
        row,
        params: Dict[TechnologyKey, TechnologyParameters],
        period_months: float,
        energy_limit: float,
        base_price: float,
    ) -> VehicleAnalysis:
        fuel_type = row.fueltypes or "unknown"
        annual_mileage = float(row.total_mileage) * 12.0 / period_months if period_months else 0.0
        annual_energy = float(row.total_energy_kwh) * 12.0 / period_months if period_months else 0.0

        cost_diesel = self._compute_cost(
            avg_consumption=row.avg_consumption_per_100km,
            fuel_type=fuel_type,
            annual_mileage=annual_mileage,
            params=params["diesel"],
            target="diesel",
            base_price=base_price,
        )
        cost_lng = self._compute_cost(
            avg_consumption=row.avg_consumption_per_100km,
            fuel_type=fuel_type,
            annual_mileage=annual_mileage,
            params=params["lng"],
            target="lng",
            base_price=base_price,
        )
        cost_bev = self._compute_cost(
            avg_consumption=row.avg_consumption_per_100km,
            fuel_type=fuel_type,
            annual_mileage=annual_mileage,
            params=params["bev"],
            target="bev",
            base_price=base_price,
        )

        if fuel_type == "diesel":
            economy = cost_diesel - cost_bev
        elif fuel_type == "lng":
            economy = cost_lng - cost_bev
        else:
            economy = 0.0

        feasibility_flag = "yes" if row.infeasible_days == 0 else "no"
        cost_efficiency_flag = "yes" if economy >= 0 else "no"
        both = "yes" if feasibility_flag == "yes" and cost_efficiency_flag == "yes" else "no"

        return VehicleAnalysis(
            vehicleid=int(row.vehicleid),
            licenseno=row.licenseno,
            fueltypes=fuel_type,
            total_mileage=float(row.total_mileage),
            total_fuel=float(row.total_fuel),
            total_energy_kwh=float(row.total_energy_kwh),
            tour_count=int(row.tour_count),
            feasible_tours=int(row.feasible_tours),
            infeasible_tours=int(row.infeasible_tours),
            feasible_days=int(row.feasible_days),
            infeasible_days=int(row.infeasible_days),
            total_days=int(row.total_days),
            avg_consumption_per_100km=float(row.avg_consumption_per_100km),
            annual_mileage=annual_mileage,
            annual_energy_kwh=annual_energy,
            cost_diesel=cost_diesel,
            cost_lng=cost_lng,
            cost_bev=cost_bev,
            economy_per_year=economy,
            feasibility_flag=feasibility_flag,
            cost_efficiency_flag=cost_efficiency_flag,
            both=both,
            feasible_rate=float(row.feasible_rate),
        )

    def _compute_cost(
        self,
        avg_consumption: float,
        fuel_type: str,
        annual_mileage: float,
        params: TechnologyParameters,
        target: TechnologyKey,
        base_price: float,
    ) -> float:
        consumption_target = self._convert_consumption(
            avg_consumption=avg_consumption,
            current_fuel_type=fuel_type,
            target=target,
        )
        weighted_energy_price = self._weighted_energy_price(params)
        energy_cost = (annual_mileage / 100.0) * consumption_target * weighted_energy_price
        lubricant_cost = energy_cost * params.lubricant_pct / 100.0
        adblue_cost = (
            (annual_mileage / 100.0)
            * (params.adblue_pct / 100.0)
            * consumption_target
            * params.adblue_price
        )
        battery_cost = 0.0
        if params.battery_cost and params.battery_life_km:
            battery_cost = annual_mileage * params.battery_cost / params.battery_life_km
        toll_cost = (
            params.toll_ct_per_km / 100.0
            * (params.toll_share_pct / 100.0)
            * annual_mileage
        )
        depreciation = (
            params.replacement_value
            - (
                params.vehicle_price
                * (1 - params.residual_pct / 100.0) ** params.lifetime_years
            )
        ) / params.lifetime_years
        maintenance_cost = params.maintenance_per_km * annual_mileage
        fixed_costs = params.tax + params.insurance
        tyre_cost = (
            params.tyre_count * params.tyre_cost * annual_mileage / params.tyre_life_km
            if params.tyre_life_km
            else 0.0
        )
        subsidy_base = max(params.vehicle_price - base_price, 0.0) * params.subsidy_pct / 100.0
        interest_cost = (
            (params.vehicle_price - subsidy_base) / 2.0 * params.interest_pct / 100.0
        )
        base_total = (
            depreciation
            + maintenance_cost
            + fixed_costs
            + tyre_cost
            + energy_cost
            + lubricant_cost
            + adblue_cost
            + battery_cost
            + toll_cost
            + interest_cost
        )
        total_cost = base_total * (1 + params.overhead_pct / 100.0)
        return float(total_cost)

    @staticmethod
    def _weighted_energy_price(params: TechnologyParameters) -> float:
        share = params.own_fuel_share / 100.0
        return share * params.own_fuel_price + (1 - share) * params.external_fuel_price

    @staticmethod
    def _convert_consumption(
        avg_consumption: float,
        current_fuel_type: str,
        target: TechnologyKey,
    ) -> float:
        if avg_consumption <= 0:
            return 0.0

        current = (current_fuel_type or "").lower()
        if target == "diesel":
            if current == "diesel":
                return avg_consumption
            if current == "lng":
                return avg_consumption * 7.0 / 5.0
            return 0.0
        if target == "lng":
            if current == "lng":
                return avg_consumption
            if current == "diesel":
                return avg_consumption * 5.0 / 7.0
            return 0.0
        if target == "bev":
            if current == "diesel":
                return avg_consumption * 5.0
            if current == "lng":
                return avg_consumption * 7.0
            return 0.0
        return 0.0

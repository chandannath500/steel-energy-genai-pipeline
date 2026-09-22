from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import zscore


def calculate_kpis(
    df: pd.DataFrame,
    energy_col: str = "Usage_kWh",
) -> dict[str, float]:
    """Calculate deterministic energy KPIs."""
    energy = pd.to_numeric(df[energy_col], errors="coerce").dropna()
    if energy.empty:
        raise ValueError("No valid energy values available for KPI calculation.")

    return {
        "total_energy_kwh": float(energy.sum()),
        "average_energy_kwh": float(energy.mean()),
        "median_energy_kwh": float(energy.median()),
        "minimum_energy_kwh": float(energy.min()),
        "peak_energy_kwh": float(energy.max()),
        "standard_deviation_kwh": float(energy.std(ddof=1) if len(energy) > 1 else 0),
        "p95_energy_kwh": float(energy.quantile(0.95)),
        "p99_energy_kwh": float(energy.quantile(0.99)),
    }


def detect_anomalies(
    df: pd.DataFrame,
    energy_col: str = "Usage_kWh",
    z_threshold: float = 3.0,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Detect statistical anomalies using a z-score threshold."""
    out = df.copy()
    values = pd.to_numeric(out[energy_col], errors="coerce")
    valid = values.notna()

    if valid.sum() < 2 or values[valid].std(ddof=1) == 0:
        out["energy_zscore"] = 0.0
        out["is_anomaly"] = False
    else:
        scores = pd.Series(np.nan, index=out.index, dtype=float)
        scores.loc[valid] = zscore(values.loc[valid])
        out["energy_zscore"] = scores.fillna(0.0)
        out["is_anomaly"] = out["energy_zscore"].abs() > z_threshold

    anomalies = out[out["is_anomaly"]].copy()
    anomaly_count = int(len(anomalies))
    anomaly_rate = float(anomaly_count / len(out) * 100) if len(out) else 0.0

    p95 = float(values.quantile(0.95))
    high_usage_count = int((values > p95).sum())

    if anomaly_count and "hour" in anomalies.columns:
        anomaly_by_hour = (
            anomalies.groupby("hour")
            .size()
            .reset_index(name="anomaly_count")
            .sort_values("anomaly_count", ascending=False)
        )
        highest_anomaly_hour = int(anomaly_by_hour.iloc[0]["hour"])
        highest_anomaly_hour_count = int(anomaly_by_hour.iloc[0]["anomaly_count"])
    else:
        anomaly_by_hour = pd.DataFrame(columns=["hour", "anomaly_count"])
        highest_anomaly_hour = None
        highest_anomaly_hour_count = 0

    summary = {
        "method": "z_score",
        "z_threshold": float(z_threshold),
        "anomaly_count": anomaly_count,
        "anomaly_percentage": anomaly_rate,
        "high_usage_threshold_kwh": p95,
        "high_usage_observations": high_usage_count,
        "highest_anomaly_hour": highest_anomaly_hour,
        "highest_anomaly_hour_count": highest_anomaly_hour_count,
    }
    return anomalies, summary


def build_operational_aggregations(
    df: pd.DataFrame,
    energy_col: str = "Usage_kWh",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build daily, hourly, load-type and weekday/weekend summaries."""
    daily = (
        df.groupby("date_only")[energy_col]
        .agg(
            total_energy="sum",
            average_energy="mean",
            peak_energy="max",
            observations="count",
        )
        .reset_index()
    )

    hourly = (
        df.groupby("hour")[energy_col]
        .agg(
            average_energy="mean",
            peak_energy="max",
            total_energy="sum",
            observations="count",
        )
        .reset_index()
    )

    if "Load_Type" in df.columns:
        load_type = (
            df.groupby("Load_Type")[energy_col]
            .agg(
                average_energy="mean",
                total_energy="sum",
                peak_energy="max",
                observations="count",
            )
            .reset_index()
            .sort_values("average_energy", ascending=False)
        )
    else:
        load_type = pd.DataFrame()

    weekday = (
        df.assign(period=np.where(df["is_weekend"], "Weekend", "Weekday"))
        .groupby("period")[energy_col]
        .agg(
            average_energy="mean",
            total_energy="sum",
            peak_energy="max",
            observations="count",
        )
        .reset_index()
    )

    return daily, hourly, load_type, weekday


def top_usage_records(
    df: pd.DataFrame,
    energy_col: str = "Usage_kWh",
    n: int = 10,
) -> list[dict[str, Any]]:
    """Return a small set of high-usage records for structured review."""
    columns = ["date", energy_col]
    for optional in ["hour", "Load_Type", "Day_of_week", "energy_zscore", "is_anomaly"]:
        if optional in df.columns and optional not in columns:
            columns.append(optional)

    top = df.nlargest(n, energy_col)[columns].copy()
    return top.to_dict(orient="records")


def top_correlations_with_energy(
    df: pd.DataFrame,
    energy_col: str = "Usage_kWh",
    n: int = 5,
) -> list[dict[str, Any]]:
    """Return the strongest numeric correlations with energy use."""
    numeric = df.select_dtypes(include="number")
    if energy_col not in numeric.columns or numeric.shape[1] < 2:
        return []

    corr = numeric.corr(numeric_only=True)[energy_col].drop(energy_col).dropna()
    ranked = corr.abs().sort_values(ascending=False).head(n)

    return [
        {
            "feature": feature,
            "correlation_with_energy": round(float(corr.loc[feature]), 4),
        }
        for feature in ranked.index
    ]


def build_structured_findings(
    df: pd.DataFrame,
    kpis: dict[str, float],
    anomaly_summary: dict[str, Any],
    daily: pd.DataFrame,
    hourly: pd.DataFrame,
    load_type: pd.DataFrame,
    weekday: pd.DataFrame,
) -> dict[str, Any]:
    """Create the compact, deterministic payload passed to the GenAI layer."""
    highest_hour_row = hourly.sort_values("average_energy", ascending=False).iloc[0]
    highest_day_row = daily.sort_values("total_energy", ascending=False).iloc[0]

    result: dict[str, Any] = {
        "dataset": {
            "record_count": int(len(df)),
            "time_start": str(df["date"].min()),
            "time_end": str(df["date"].max()),
        },
        "energy_kpis": {
            key: round(float(value), 2)
            for key, value in kpis.items()
        },
        "anomaly_analysis": {
            key: (round(float(value), 2) if isinstance(value, (float, np.floating)) else value)
            for key, value in anomaly_summary.items()
        },
        "operational_patterns": {
            "highest_average_energy_hour": int(highest_hour_row["hour"]),
            "highest_average_energy_hour_kwh": round(float(highest_hour_row["average_energy"]), 2),
            "highest_total_energy_date": str(highest_day_row["date_only"]),
            "highest_total_energy_date_kwh": round(float(highest_day_row["total_energy"]), 2),
        },
        "weekday_weekend": [
            {
                key: (round(float(value), 2) if isinstance(value, (float, np.floating)) else value)
                for key, value in row.items()
            }
            for row in weekday.to_dict(orient="records")
        ],
        "top_usage_records": top_usage_records(df),
        "top_numeric_correlations_with_energy": top_correlations_with_energy(df),
    }

    if not load_type.empty:
        result["load_type_analysis"] = [
            {
                key: (round(float(value), 2) if isinstance(value, (float, np.floating)) else value)
                for key, value in row.items()
            }
            for row in load_type.to_dict(orient="records")
        ]

    power_factor_candidates = [
        c for c in df.columns
        if "power_factor" in c.lower()
    ]
    if power_factor_candidates:
        for column in power_factor_candidates[:2]:
            series = pd.to_numeric(df[column], errors="coerce")
            result.setdefault("power_factor_metrics", {})[column] = {
                "average": round(float(series.mean()), 4),
                "minimum": round(float(series.min()), 4),
                "maximum": round(float(series.max()), 4),
            }

    return result

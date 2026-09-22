from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    return path


def create_charts(
    df: pd.DataFrame,
    daily: pd.DataFrame,
    hourly: pd.DataFrame,
    load_type: pd.DataFrame,
    output_dir: str | Path,
    energy_col: str = "Usage_kWh",
) -> list[Path]:
    """Create five business-oriented charts."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    # 1. Energy trend + P95 threshold + anomalies
    plt.figure(figsize=(13, 5))
    plt.plot(df["date"], df[energy_col], linewidth=0.7, label="Energy")
    p95 = df[energy_col].quantile(0.95)
    plt.axhline(p95, linestyle="--", linewidth=1.2, label="P95 threshold")
    if "is_anomaly" in df.columns and df["is_anomaly"].any():
        anomalous = df[df["is_anomaly"]]
        plt.scatter(
            anomalous["date"],
            anomalous[energy_col],
            s=14,
            label="Statistical anomaly",
        )
    plt.title("Steel Industry Energy Consumption Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy Consumption (kWh)")
    plt.legend()
    paths.append(_save(output_dir / "01_energy_consumption_trend.png"))

    # 2. Daily energy profile
    plt.figure(figsize=(13, 5))
    plt.plot(daily["date_only"], daily["total_energy"], linewidth=1.6)
    plt.title("Daily Energy Consumption")
    plt.xlabel("Date")
    plt.ylabel("Total Energy (kWh)")
    plt.xticks(rotation=45)
    paths.append(_save(output_dir / "02_daily_energy_consumption.png"))

    # 3. Hourly profile
    plt.figure(figsize=(10, 5))
    hourly_sorted = hourly.sort_values("hour")
    plt.plot(
        hourly_sorted["hour"],
        hourly_sorted["average_energy"],
        marker="o",
        linewidth=1.6,
    )
    plt.title("Average Energy Consumption by Hour")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average Energy (kWh)")
    plt.xticks(range(24))
    plt.grid(alpha=0.25)
    paths.append(_save(output_dir / "03_hourly_energy_pattern.png"))

    # 4. Load-type average energy
    plt.figure(figsize=(9, 5))
    if not load_type.empty and "Load_Type" in load_type.columns:
        plot_df = load_type.sort_values("average_energy")
        plt.bar(plot_df["Load_Type"], plot_df["average_energy"])
        plt.title("Average Energy Consumption by Load Type")
        plt.xlabel("Load Type")
        plt.ylabel("Average Energy (kWh)")
        plt.xticks(rotation=0)
    else:
        fallback = hourly.sort_values("average_energy", ascending=False).head(10)
        plt.bar(fallback["hour"].astype(str), fallback["average_energy"])
        plt.title("Top Hours by Average Energy Consumption")
        plt.xlabel("Hour")
        plt.ylabel("Average Energy (kWh)")
    paths.append(_save(output_dir / "04_load_type_energy.png"))

    # 5. Energy vs power factor, with correlation fallback
    power_factor_candidates = [
        c for c in df.columns if "power_factor" in c.lower()
    ]

    if power_factor_candidates:
        pf_col = power_factor_candidates[0]
        plt.figure(figsize=(9, 6))
        plt.scatter(
            df[pf_col],
            df[energy_col],
            alpha=0.35,
            s=10,
        )
        plt.title(f"Energy Consumption vs {pf_col}")
        plt.xlabel(pf_col)
        plt.ylabel("Energy Consumption (kWh)")
    else:
        plt.figure(figsize=(10, 7))
        numeric = df.select_dtypes(include="number")
        if numeric.shape[1] >= 2:
            plt.imshow(numeric.corr(), aspect="auto")
            plt.colorbar(label="Correlation")
            plt.title("Correlation Matrix of Numeric Variables")
            plt.xticks(range(len(numeric.columns)), numeric.columns, rotation=90, fontsize=7)
            plt.yticks(range(len(numeric.columns)), numeric.columns, fontsize=7)
        else:
            plt.text(0.5, 0.5, "Not enough numeric variables", ha="center", va="center")
            plt.axis("off")

    paths.append(_save(output_dir / "05_energy_power_factor_relationship.png"))

    return paths

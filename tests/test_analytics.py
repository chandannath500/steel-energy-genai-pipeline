from __future__ import annotations

import pandas as pd

from src.analytics import (
    build_operational_aggregations,
    calculate_kpis,
    detect_anomalies,
)
from src.data_loader import prepare_dates, standardize_columns
from src.data_quality import clean_dataset


def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2018-01-01", periods=10, freq="15min"),
            "Usage_kWh": [10, 11, 12, 13, 14, 15, 16, 17, 18, 1000],
            "Load_Type": ["Light Load"] * 10,
        }
    )


def test_standardize_columns():
    df = pd.DataFrame({"Lagging_Current_Reactive.Power_kVarh": [1]})
    out = standardize_columns(df)
    assert out.columns.tolist() == ["Lagging_Current_Reactive_Power_kVarh"]


def test_prepare_dates_creates_time_features():
    out = prepare_dates(sample_df())
    assert "hour" in out.columns
    assert "day_of_week" in out.columns
    assert "is_weekend" in out.columns
    assert out["date"].notna().all()


def test_clean_dataset_reports_duplicates():
    df = pd.concat([sample_df(), sample_df().iloc[[0]]], ignore_index=True)
    cleaned, report = clean_dataset(df)
    assert len(cleaned) == 10
    assert report.duplicate_rows_removed == 1


def test_calculate_kpis():
    kpis = calculate_kpis(sample_df())
    assert kpis["peak_energy_kwh"] == 1000
    assert kpis["minimum_energy_kwh"] == 10


def test_detect_anomalies_returns_expected_columns():
    df = prepare_dates(sample_df())
    anomalies, summary = detect_anomalies(df, z_threshold=2.5)
    assert "is_anomaly" in anomalies.columns
    assert "anomaly_count" in summary
    assert summary["anomaly_count"] >= 1


def test_operational_aggregations():
    df = prepare_dates(sample_df())
    daily, hourly, load_type, weekday = build_operational_aggregations(df)
    assert len(daily) == 1
    assert len(hourly) == 3
    assert not load_type.empty
    assert not weekday.empty

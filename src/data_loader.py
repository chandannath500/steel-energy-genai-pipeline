from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load a CSV dataset and fail fast on missing/empty files."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Run `python -m src.download_data` "
            "or place Steel_industry_data.csv in data/raw/."
        )

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("The dataset is empty.")
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to safe, consistent Python/SQL-friendly names."""
    out = df.copy()
    cleaned = []

    for column in out.columns.astype(str):
        name = re.sub(r"[^0-9A-Za-z]+", "_", column.strip())
        name = re.sub(r"_+", "_", name).strip("_")
        cleaned.append(name)

    out.columns = cleaned
    return out


def prepare_dates(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Parse timestamps and add reusable time dimensions."""
    out = df.copy()
    if date_col not in out.columns:
        raise KeyError(f"Expected timestamp column '{date_col}' not found.")

    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
    out = (
        out.dropna(subset=[date_col])
        .sort_values(date_col)
        .reset_index(drop=True)
    )

    out["date_only"] = out[date_col].dt.date
    out["hour"] = out[date_col].dt.hour
    out["day_of_week"] = out[date_col].dt.day_name()
    out["month"] = out[date_col].dt.month
    out["week_of_year"] = out[date_col].dt.isocalendar().week.astype(int)
    out["is_weekend"] = out[date_col].dt.dayofweek >= 5

    return out

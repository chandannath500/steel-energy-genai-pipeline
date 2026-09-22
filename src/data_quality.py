from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


@dataclass
class QualityReport:
    rows_before: int
    rows_after: int
    columns: int
    duplicate_rows_removed: int
    invalid_timestamps_removed: int
    invalid_energy_values_removed: int
    negative_energy_values_observed: int
    remaining_missing_values: int

    def to_dict(self) -> dict:
        return asdict(self)


def validate_required_columns(
    df: pd.DataFrame,
    required: list[str] | tuple[str, ...],
) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def clean_dataset(
    df: pd.DataFrame,
    energy_col: str = "Usage_kWh",
) -> tuple[pd.DataFrame, QualityReport]:
    """Apply conservative cleaning rules and return a quality audit."""
    rows_before = len(df)
    out = df.copy()

    duplicate_rows_removed = int(out.duplicated().sum())
    out = out.drop_duplicates()

    if "date" not in out.columns:
        raise ValueError("Expected 'date' column after standardization.")

    parsed_dates = pd.to_datetime(out["date"], errors="coerce")
    invalid_timestamps_removed = int(parsed_dates.isna().sum())
    out["date"] = parsed_dates
    out = out.dropna(subset=["date"])

    if energy_col not in out.columns:
        raise ValueError(f"Expected energy column '{energy_col}'.")

    numeric_energy = pd.to_numeric(out[energy_col], errors="coerce")
    invalid_energy_values_removed = int(numeric_energy.isna().sum())
    negative_energy_values_observed = int((numeric_energy < 0).sum())
    out[energy_col] = numeric_energy
    out = out.dropna(subset=[energy_col])

    remaining_missing = int(out.isna().sum().sum())

    report = QualityReport(
        rows_before=rows_before,
        rows_after=len(out),
        columns=out.shape[1],
        duplicate_rows_removed=duplicate_rows_removed,
        invalid_timestamps_removed=invalid_timestamps_removed,
        invalid_energy_values_removed=invalid_energy_values_removed,
        negative_energy_values_observed=negative_energy_values_observed,
        remaining_missing_values=remaining_missing,
    )
    return out.reset_index(drop=True), report

from __future__ import annotations

from pathlib import Path


def build_markdown_report(
    analytics: dict,
    ai_insights: str,
    chart_paths: list[Path],
) -> str:
    dataset = analytics["dataset"]
    kpis = analytics["energy_kpis"]
    anomaly = analytics["anomaly_analysis"]
    patterns = analytics["operational_patterns"]
    quality = analytics.get("data_quality", {})

    chart_lines = "\n\n".join(
        f"### {idx}. {path.stem.replace('_', ' ').title()}\n\n"
        f"![{path.stem}](../charts/{path.name})"
        for idx, path in enumerate(chart_paths, start=1)
    )

    return f"""# Steel Industry Energy Monitoring Report

## Dataset

- Records analyzed: **{dataset['record_count']:,}**
- Time range: **{dataset['time_start']}** to **{dataset['time_end']}**

## Data Quality

| Check | Result |
|---|---:|
| Rows before cleaning | {quality.get('rows_before', 'N/A'):,} |
| Rows after cleaning | {quality.get('rows_after', 'N/A'):,} |
| Duplicate rows removed | {quality.get('duplicate_rows_removed', 'N/A'):,} |
| Invalid timestamps removed | {quality.get('invalid_timestamps_removed', 'N/A'):,} |
| Invalid energy values removed | {quality.get('invalid_energy_values_removed', 'N/A'):,} |
| Negative energy values observed | {quality.get('negative_energy_values_observed', 'N/A'):,} |
| Remaining missing values | {quality.get('remaining_missing_values', 'N/A'):,} |

## KPI Summary

| KPI | Value |
|---|---:|
| Total Energy | {kpis['total_energy_kwh']:,.2f} kWh |
| Average Energy | {kpis['average_energy_kwh']:,.2f} kWh |
| Median Energy | {kpis['median_energy_kwh']:,.2f} kWh |
| Minimum Energy | {kpis['minimum_energy_kwh']:,.2f} kWh |
| Peak Energy | {kpis['peak_energy_kwh']:,.2f} kWh |
| P95 Energy | {kpis['p95_energy_kwh']:,.2f} kWh |
| P99 Energy | {kpis['p99_energy_kwh']:,.2f} kWh |
| Standard Deviation | {kpis['standard_deviation_kwh']:,.2f} kWh |

## Anomaly Analysis

- Method: **{anomaly['method']}**
- Z-score threshold: **{anomaly['z_threshold']}**
- Statistical anomalies detected: **{anomaly['anomaly_count']:,}**
- Anomaly rate: **{anomaly['anomaly_percentage']:.2f}%**
- High-usage threshold (P95): **{anomaly['high_usage_threshold_kwh']:,.2f} kWh**
- High-usage observations: **{anomaly['high_usage_observations']:,}**
- Hour with most anomalies: **{anomaly['highest_anomaly_hour']}**

## Operational Patterns

- Highest average-energy hour: **{patterns['highest_average_energy_hour']}:00**
- Average energy at that hour: **{patterns['highest_average_energy_hour_kwh']:,.2f} kWh**
- Highest total-energy date: **{patterns['highest_total_energy_date']}**
- Total energy on that date: **{patterns['highest_total_energy_date_kwh']:,.2f} kWh**

## GenAI Insight Generation

{ai_insights}

## Visual Analysis

{chart_lines}

## Architecture

`Raw Data → Data Quality → Python Analytics → Anomaly Detection → Structured Findings JSON → LangChain → LLM → Business Insights → Slack`

## Important Design Boundary

Python and SQL perform deterministic calculations. The GenAI layer receives the structured findings rather than the complete raw dataset. This makes the numerical results reproducible and keeps the LLM focused on interpretation and communication.
"""


def save_report(content: str, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path

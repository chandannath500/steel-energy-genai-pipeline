from __future__ import annotations

import json
import logging

from src.analytics import (
    build_operational_aggregations,
    build_structured_findings,
    calculate_kpis,
    detect_anomalies,
)
from src.config import (
    DATA_PATH,
    CHARTS_DIR,
    ENABLE_SLACK,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    PROCESSED_DIR,
    REPORTS_DIR,
    SLACK_BOT_TOKEN,
    SLACK_CHANNEL_ID,
)
from src.data_loader import load_csv, prepare_dates, standardize_columns
from src.data_quality import clean_dataset, validate_required_columns
from src.report import build_markdown_report, save_report
from src.visualization import create_charts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

CLEANED_DATA_FILE = PROCESSED_DIR / "cleaned_energy_data.csv"
ANALYTICS_JSON_FILE = PROCESSED_DIR / "analytics_results.json"
QUALITY_JSON_FILE = PROCESSED_DIR / "data_quality_report.json"
REPORT_FILE = REPORTS_DIR / "steel_energy_report.md"


def main() -> None:
    logger.info("Loading dataset from %s", DATA_PATH)
    df = standardize_columns(load_csv(DATA_PATH))

    validate_required_columns(df, required=["date", "Usage_kWh"])

    df, quality = clean_dataset(df, energy_col="Usage_kWh")
    df = prepare_dates(df, date_col="date")

    logger.info(
        "Data quality: %s rows before, %s after, %s duplicates removed",
        quality.rows_before,
        quality.rows_after,
        quality.duplicate_rows_removed,
    )

    df.to_csv(CLEANED_DATA_FILE, index=False)
    QUALITY_JSON_FILE.write_text(
        json.dumps(quality.to_dict(), indent=2),
        encoding="utf-8",
    )

    kpis = calculate_kpis(df)
    anomalies, anomaly_summary = detect_anomalies(df)
    daily, hourly, load_type, weekday = build_operational_aggregations(df)

    analytics_results = build_structured_findings(
        df=df,
        kpis=kpis,
        anomaly_summary=anomaly_summary,
        daily=daily,
        hourly=hourly,
        load_type=load_type,
        weekday=weekday,
    )
    analytics_results["data_quality"] = quality.to_dict()

    ANALYTICS_JSON_FILE.write_text(
        json.dumps(analytics_results, indent=2, default=str),
        encoding="utf-8",
    )

    chart_paths = create_charts(
        df=df,
        daily=daily,
        hourly=hourly,
        load_type=load_type,
        output_dir=CHARTS_DIR,
    )
    logger.info("Generated %s charts", len(chart_paths))

    if OPENAI_API_KEY:
        from src.genai import generate_insights

        logger.info("Generating business insights with LangChain + %s", OPENAI_MODEL)
        try:
            ai_insights = generate_insights(
                analytics_results=analytics_results,
                api_key=OPENAI_API_KEY,
                model_name=OPENAI_MODEL,
            )
        except Exception as exc:
            logger.exception("GenAI step failed")
            ai_insights = (
                "GenAI insight generation failed for this run. "
                f"Deterministic analytics and visualizations were completed. Error: {exc}"
            )
    else:
        logger.warning("OPENAI_API_KEY not configured; skipping GenAI step")
        ai_insights = (
            "GenAI was not executed because OPENAI_API_KEY is not configured. "
            "The deterministic Python analytics and visualizations were still generated."
        )

    report = build_markdown_report(
        analytics=analytics_results,
        ai_insights=ai_insights,
        chart_paths=chart_paths,
    )
    save_report(report, REPORT_FILE)

    if ENABLE_SLACK:
        from src.slack import send_report

        if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
            raise ValueError(
                "ENABLE_SLACK=true but Slack credentials are missing. "
                "Set SLACK_BOT_TOKEN and SLACK_CHANNEL_ID in .env."
            )

        slack_text = (
            "🏭 STEEL INDUSTRY ENERGY MONITORING REPORT\n\n"
            f"Records analyzed: {len(df):,}\n"
            f"Total energy: {kpis['total_energy_kwh']:,.2f} kWh\n"
            f"Average energy: {kpis['average_energy_kwh']:,.2f} kWh\n"
            f"Peak energy: {kpis['peak_energy_kwh']:,.2f} kWh\n"
            f"Statistical anomalies: {anomaly_summary['anomaly_count']:,} "
            f"({anomaly_summary['anomaly_percentage']:.2f}%)\n\n"
            "🤖 GENAI INSIGHTS\n"
            f"{ai_insights}"
        )
        send_report(
            bot_token=SLACK_BOT_TOKEN,
            channel_id=SLACK_CHANNEL_ID,
            summary_text=slack_text,
            chart_paths=chart_paths,
        )
        logger.info("Slack delivery completed")

    logger.info("Pipeline completed successfully")
    logger.info("Cleaned data: %s", CLEANED_DATA_FILE)
    logger.info("Analytics JSON: %s", ANALYTICS_JSON_FILE)
    logger.info("Report: %s", REPORT_FILE)


if __name__ == "__main__":
    main()

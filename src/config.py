from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHARTS_DIR = ROOT_DIR / "charts"
REPORTS_DIR = ROOT_DIR / "reports"

for path in (RAW_DIR, PROCESSED_DIR, CHARTS_DIR, REPORTS_DIR):
    path.mkdir(parents=True, exist_ok=True)

DATA_PATH = Path(
    os.getenv("DATA_PATH", str(RAW_DIR / "Steel_industry_data.csv"))
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")
ENABLE_SLACK = os.getenv("ENABLE_SLACK", "false").lower() == "true"

MYSQL_URL = os.getenv("MYSQL_URL", "")

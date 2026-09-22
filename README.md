# Automated Steel Industry Energy Monitoring & GenAI Insight Pipeline

An end-to-end analytics project that combines **Python, Pandas, SQL, statistical anomaly detection, LangChain, an LLM, Tableau and Slack automation** to turn repetitive industrial energy data into structured, decision-ready insights.

> **Core design principle:** deterministic analytics first, generative interpretation second.

## Business Problem

Industrial energy data can contain thousands of repeated measurements. Reviewing raw observations, calculating KPIs, finding unusual periods, preparing charts and writing management summaries manually is repetitive and difficult to scale.

This project demonstrates how that workflow can be automated without asking an LLM to perform the core numerical analysis.

## What I Built

The pipeline:

1. Downloads the public steel-industry energy dataset from UCI.
2. Standardizes and validates the incoming data.
3. Performs conservative data cleaning and records a quality audit.
4. Calculates deterministic energy KPIs in Python.
5. Builds daily, hourly, load-type and weekday/weekend summaries.
6. Detects statistical anomalies using z-scores.
7. Generates five operational visualizations.
8. Converts the analytical results into a compact structured JSON payload.
9. Sends only those validated findings into a LangChain LLM workflow.
10. Generates an operations-friendly insight narrative.
11. Produces a Markdown report.
12. Optionally delivers the report summary and charts to Slack.
13. Provides SQL scripts and a Tableau dashboard specification for BI analysis.

## Architecture

```text
                     ┌────────────────────────┐
                     │  UCI Steel Energy Data │
                     │      35,040 rows       │
                     └────────────┬───────────┘
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │ Data Quality & Cleaning│
                     │ duplicates / timestamps│
                     │ numeric validation     │
                     └────────────┬───────────┘
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │   Python Analytics     │
                     │ KPIs / aggregations    │
                     │ statistics / patterns  │
                     └────────────┬───────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼                                 ▼
        ┌──────────────────┐              ┌──────────────────┐
        │ Anomaly Detection│              │ 5 Visualizations │
        └─────────┬────────┘              └─────────┬────────┘
                  │                                 │
                  └────────────────┬────────────────┘
                                   ▼
                      ┌────────────────────────┐
                      │ Structured Findings   │
                      │      JSON payload     │
                      └────────────┬───────────┘
                                   │
                                   ▼
                      ┌────────────────────────┐
                      │ LangChain Prompt Chain │
                      │   + selected LLM       │
                      └────────────┬───────────┘
                                   │
                                   ▼
                      ┌────────────────────────┐
                      │ Business Insights      │
                      └────────────┬───────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
              ┌──────────────┐           ┌──────────────┐
              │ Slack        │           │ Tableau      │
              │ Automation   │           │ Exploration  │
              └──────────────┘           └──────────────┘
```

## Why This GenAI Architecture?

The LLM **does not receive the complete raw dataset**.

Instead:

```text
35,040 raw observations
        ↓
Python / SQL calculations
        ↓
KPI + anomaly + aggregation layer
        ↓
Structured analytics_results.json
        ↓
LangChain workflow
        ↓
LLM
        ↓
Business-oriented narrative
```

This creates a clean responsibility split:

| Layer | Responsibility |
|---|---|
| Data ingestion | Retrieve source data |
| Data quality | Validate and clean |
| SQL | Reproducible extraction and aggregation |
| Python/Pandas | KPI calculations and analysis |
| Statistics | Detect statistical anomalies |
| Visualization | Show operational patterns |
| LangChain | Orchestrate prompt → model → output |
| LLM | Interpret validated findings and communicate them |
| Slack | Automated delivery |
| Tableau | Interactive BI exploration |

## Dataset

This repository uses the **Steel Industry Energy Consumption** dataset from the UCI Machine Learning Repository, Dataset 851. UCI lists **35,040 instances** and the dataset is licensed under **CC BY 4.0**.

See [DATA_SOURCES.md](DATA_SOURCES.md) for the source, DOI and attribution details.

## Repository Structure

```text
steel-energy-genai/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── data/
│   ├── raw/
│   │   └── README.md
│   └── processed/
│       └── README.md
│
├── charts/
│   └── README.md
│
├── reports/
│   └── README.md
│
├── sql/
│   ├── create_tables.sql
│   ├── kpi_queries.sql
│   └── anomaly_queries.sql
│
├── src/
│   ├── analytics.py
│   ├── config.py
│   ├── data_loader.py
│   ├── data_quality.py
│   ├── download_data.py
│   ├── genai.py
│   ├── load_to_mysql.py
│   ├── main.py
│   ├── report.py
│   ├── slack.py
│   └── visualization.py
│
├── tests/
│   ├── conftest.py
│   └── test_analytics.py
│
├── tableau/
│   └── README.md
│
├── docs/
│   └── INTERVIEW_GUIDE.md
│
├── .env.example
├── .gitignore
├── DATA_SOURCES.md
├── LICENSE
├── README.md
└── requirements.txt
```

## Setup

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/steel-energy-genai.git
cd steel-energy-genai
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`.

Windows:

```bash
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Do **not** commit `.env` or any API keys.

## Download the Data

```bash
python -m src.download_data
```

The file will be created at:

```text
data/raw/Steel_industry_data.csv
```

## Run the Pipeline

The deterministic pipeline can run without an OpenAI key:

```bash
python -m src.main
```

With `OPENAI_API_KEY` configured, the same run also performs the LangChain insight-generation step.

Generated files include:

```text
data/processed/cleaned_energy_data.csv
data/processed/analytics_results.json
data/processed/data_quality_report.json
charts/01_energy_consumption_trend.png
charts/02_daily_energy_consumption.png
charts/03_hourly_energy_pattern.png
charts/04_load_type_energy.png
charts/05_energy_power_factor_relationship.png
reports/steel_energy_report.md
```

## SQL Layer

The `sql/` directory contains reproducible queries for:

- Total and average energy
- Peak and minimum energy
- Daily energy profile
- Hourly energy profile
- Load-type comparison
- High-usage operational review

To load the source dataset into MySQL:

```bash
python -m src.load_to_mysql
```

Set `MYSQL_URL` in `.env` first.

## GenAI Layer

The GenAI module uses LangChain runnable composition:

```text
Structured Findings JSON
        ↓
ChatPromptTemplate
        ↓
ChatOpenAI
        ↓
StrOutputParser
        ↓
Business Insight Narrative
```

The important architectural boundary is that the LLM receives **validated analytical findings**, not the full raw DataFrame.

The prompt instructs the model to:

- use only supplied findings
- avoid invented or unsupported values
- distinguish observations from recommendations
- treat recommendations as investigation areas rather than confirmed root causes

## Slack Automation

Set:

```env
ENABLE_SLACK=true
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL_ID=C...
```

The pipeline posts the summary and uploads the five generated charts.

## Tableau

Use either the cleaned CSV or the MySQL table as the Tableau source.

Recommended dashboard sections:

- KPI cards
- Energy trend
- Daily energy
- Hourly energy
- Load type comparison
- Energy vs power factor
- Anomaly review

See [tableau/README.md](tableau/README.md).

## Testing

Run:

```bash
pytest -q
```

A GitHub Actions workflow in `.github/workflows/tests.yml` also runs the tests on pushes and pull requests.

## Security

- API keys are read from environment variables.
- `.env` is ignored by Git.
- Raw and generated data are ignored by Git by default.
- No credentials are required to inspect the repository.

## Limitations

This is a portfolio analytics project built from a public dataset. The anomaly detector is intentionally transparent and statistical; it does not establish equipment failure or causal root causes. The LLM layer is also deliberately constrained to interpretation of deterministic findings.

## Production Improvements

A production implementation could add:

- database or streaming ingestion
- scheduled execution
- data-quality monitoring and alerts
- more robust anomaly detection by equipment/operating context
- LLM evaluation and observability
- human approval for high-impact recommendations
- governed BI datasets and role-based access
- historical alert tracking and incident feedback

## Interview Focus

The project is designed to demonstrate that I understand the difference between:

1. **Analytics:** calculating what happened in the data.
2. **Anomaly detection:** flagging statistically unusual observations.
3. **GenAI:** interpreting validated findings and communicating them in business language.
4. **Automation:** delivering the result to stakeholders without repeated manual effort.

For interview preparation, see [docs/INTERVIEW_GUIDE.md](docs/INTERVIEW_GUIDE.md).

## Author

**Chandan Nath**

Data Analytics | SQL | Python | Tableau | GenAI Automation

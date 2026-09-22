# Interview Guide

## 30-second project explanation

> I built an automated steel-industry energy monitoring and insight pipeline using Python, SQL, statistical anomaly detection, LangChain, an LLM, Tableau and Slack. The pipeline validates and cleans the data, calculates deterministic KPIs, identifies statistical anomalies, generates five business-oriented visualizations, converts the findings into a structured JSON payload, and passes only those validated findings to a LangChain LLM workflow for interpretation. The final insights and charts can then be delivered automatically through Slack, while Tableau provides interactive exploration.

## Why did you separate Python from GenAI?

Python is better suited to deterministic calculations such as totals, averages, percentiles and anomaly detection. The LLM is used for interpretation and communication. Keeping those responsibilities separate makes the numerical layer reproducible and easier to test.

## Why didn't you send all 35,040 rows to the LLM?

Sending the complete raw dataset would be unnecessary for this use case. I first reduced the data to validated KPIs, aggregations, anomaly summaries and a small set of high-usage observations. The LLM receives that structured analytical context rather than the full raw dataset.

## How did you detect anomalies?

I used a z-score threshold of 3 as a transparent statistical starting point. I also calculated the 95th percentile to identify high-usage observations. These are statistical signals, not proof of equipment failure or a root cause.

## How did you address hallucination risk?

The prompt explicitly limits the model to the supplied analytical findings, tells it not to invent or recalculate unsupported values, and keeps numerical calculations outside the LLM layer.

## What does LangChain do here?

LangChain provides the reusable prompt-to-model workflow. The chain takes the structured JSON findings, sends them through the prompt template to the selected LLM, and parses the resulting business narrative.

## What is automated?

Data loading, cleaning, KPI calculation, anomaly detection, five chart generations, report generation, optional GenAI insight generation and optional Slack delivery.

## What would you improve in production?

I would move ingestion from a static CSV to a plant database or streaming source, schedule recurring runs, add model observability and evaluation, use domain-calibrated anomaly detection, add alert thresholds and ownership, and connect the governed dataset to the BI layer.

## Important wording

Say **"statistical anomaly"** or **"high-usage observation"**, not **"equipment failure"**, unless the source data actually proves a failure.

Say **"area to investigate"** rather than claiming a confirmed root cause from an observational dataset.

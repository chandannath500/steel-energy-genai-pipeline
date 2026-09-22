from __future__ import annotations

import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


SYSTEM_PROMPT = """
You are a senior industrial data analyst supporting a steel manufacturing operation.

You will receive ONLY validated analytical findings produced by a Python analytics pipeline.
The Python layer has already performed the numerical calculations and statistical anomaly detection.
Your role is to interpret those findings and communicate them clearly.

Rules:
- Use only the supplied analytical findings.
- Do not invent, estimate, or recalculate unsupported values.
- Do not claim to have reviewed the raw records directly.
- Distinguish observed facts from recommendations.
- Recommendations must be framed as investigation areas, not confirmed root causes.
- Use exact values from the supplied findings when useful.
- Focus on operationally useful patterns.
- Mention uncertainty where the evidence is insufficient.

Return exactly these sections:
1. Executive Summary
2. Key Findings
3. Anomaly Analysis
4. Operational Observations
5. Recommended Actions
"""


def build_chain(api_key: str, model_name: str):
    """Build a LangChain prompt → model → parser workflow."""
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not configured. Set it in .env before enabling GenAI."
        )

    model = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=api_key,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "Validated analytical findings:\n{analytics_json}",
            ),
        ]
    )

    return prompt | model | StrOutputParser()


def generate_insights(
    analytics_results: dict,
    api_key: str,
    model_name: str,
) -> str:
    """Generate business insights from compact, deterministic analytics output."""
    chain = build_chain(api_key, model_name)
    payload = json.dumps(analytics_results, indent=2, default=str)
    return chain.invoke({"analytics_json": payload})

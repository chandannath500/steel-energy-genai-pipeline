from __future__ import annotations

from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def send_report(
    bot_token: str,
    channel_id: str,
    summary_text: str,
    chart_paths: list[Path],
) -> None:
    """Publish the summary and generated chart files to Slack."""
    if not bot_token or not channel_id:
        raise ValueError(
            "SLACK_BOT_TOKEN and SLACK_CHANNEL_ID are required to send a Slack report."
        )

    client = WebClient(token=bot_token)

    try:
        client.chat_postMessage(channel=channel_id, text=summary_text)
        for chart_path in chart_paths:
            client.files_upload_v2(
                channel=channel_id,
                file=str(chart_path),
                title=chart_path.stem,
                initial_comment=f"📈 {chart_path.stem.replace('_', ' ').title()}",
            )
    except SlackApiError as exc:
        error = exc.response.get("error", "unknown_error")
        raise RuntimeError(f"Slack API request failed: {error}") from exc

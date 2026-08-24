import os
import json

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is missing from .env"
    )


client = Groq(
    api_key=api_key
)


def explain_anomaly(log):

    prompt = f"""
You are a production log analysis assistant.

The application has already detected this log as an anomaly.

You MUST NOT decide whether the log is anomalous.

Your job is only to explain why the already-detected
anomaly is important.

Analyze the following log:

Timestamp: {log["timestamp"]}
Event Type: {log["event_type"]}
Severity: {log["severity"]}
Source: {log["source"]}
Status: {log["status"]}
Message: {log["message"]}

Anomaly Score:
{log["anomaly_score"]}

Detection Reason:
{log["anomaly_reason"]}

Return ONLY valid JSON in this exact format:

{{
    "explanation": "Explain what happened",
    "root_cause": "Give the most likely root cause",
    "next_step": "Give a practical recommended next step"
}}
"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": "You are a production log analysis assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
    )

    content = response.choices[0].message.content

    try:

        return json.loads(content)

    except json.JSONDecodeError:

        return {
            "explanation": content,
            "root_cause": "Unable to parse structured response.",
            "next_step": "Review the anomaly manually."
        }
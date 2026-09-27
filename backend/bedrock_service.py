import json
import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_PROFILE = os.getenv("AWS_PROFILE")
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "apac.amazon.nova-lite-v1:0",
)

SYSTEM_PROMPT = """You are OpsPilot AI, a cautious DevOps incident-response assistant.

Analyze ONLY the incident evidence and runbook context provided by the application.
Do not invent logs, metrics, deployments, or root causes that are not supported by the input.
Clearly distinguish a probable cause from a confirmed cause.
Treat the runbook as troubleshooting guidance, not proof that its diagnosis is correct.
Do not execute or imply that you executed production changes.

Return VALID JSON ONLY with exactly these keys:
{
  "summary": "short incident summary",
  "probable_cause": "most likely cause with uncertainty stated",
  "impact": "likely operational/user impact",
  "recommended_actions": ["3 to 5 ordered investigation steps"],
  "rollback_consideration": "whether rollback should be considered and why",
  "confidence_percent": 0
}

confidence_percent must be an integer from 0 to 100.
"""


def _session():
    if AWS_PROFILE:
        return boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION,
        )
    return boto3.Session(region_name=AWS_REGION)


def _extract_json(text: str) -> dict:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1).replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise RuntimeError("Bedrock returned a response that did not contain valid JSON.")
        return json.loads(cleaned[start:end + 1])


def analyze_incident_with_bedrock(*, incident, service, runbook=None) -> dict:
    client = _session().client("bedrock-runtime")

    evidence_lines = "\n".join(
        f"- {item}" for item in (incident.evidence or [])
    ) or "- No evidence recorded"

    if runbook:
        runbook_context = f"""Runbook title: {runbook.title}
Runbook problem type: {runbook.problem_type}
Runbook description: {runbook.description}
Runbook content:
{runbook.content}
"""
    else:
        runbook_context = "No matching runbook was retrieved."

    prompt = f"""Analyze this DevOps incident.

Service: {service.name}
Environment: {service.environment}
Service status: {service.status}

Incident ID: {incident.id}
Title: {incident.title}
Severity: {incident.severity}
Incident status: {incident.status}
Summary: {incident.summary}

Evidence:
{evidence_lines}

Recent deployment:
{incident.recent_deployment or "No recent deployment recorded"}

Retrieved troubleshooting context:
{runbook_context}

Use only the context above. Return the required JSON object.
"""

    response = client.converse(
        modelId=BEDROCK_MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        inferenceConfig={
            "maxTokens": 800,
            "temperature": 0.2,
            "topP": 0.9,
        },
    )

    content = response["output"]["message"]["content"]
    output_text = next(
        (part["text"] for part in content if "text" in part),
        "",
    )

    data = _extract_json(output_text)

    required = {
        "summary",
        "probable_cause",
        "impact",
        "recommended_actions",
        "rollback_consideration",
        "confidence_percent",
    }
    missing = required - set(data)
    if missing:
        raise RuntimeError(
            "Bedrock response is missing required fields: "
            + ", ".join(sorted(missing))
        )

    if not isinstance(data["recommended_actions"], list):
        raise RuntimeError("Bedrock recommended_actions must be a list.")

    try:
        confidence = int(data["confidence_percent"])
    except (TypeError, ValueError):
        confidence = 0
    data["confidence_percent"] = max(0, min(100, confidence))

    usage = response.get("usage", {})
    metrics = response.get("metrics", {})

    data["model_id"] = BEDROCK_MODEL_ID
    data["input_tokens"] = int(usage.get("inputTokens", 0) or 0)
    data["output_tokens"] = int(usage.get("outputTokens", 0) or 0)
    data["total_tokens"] = int(usage.get("totalTokens", 0) or 0)
    data["latency_ms"] = int(metrics.get("latencyMs", 0) or 0)
    data["runbook_id"] = runbook.id if runbook else None
    data["runbook_title"] = runbook.title if runbook else None

    return data

import json
import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_PROFILE = os.getenv("AWS_PROFILE")
EMBEDDING_MODEL_ID = os.getenv(
    "EMBEDDING_MODEL_ID",
    "amazon.titan-embed-text-v2:0",
)
EMBEDDING_DIMENSIONS = 512


def _session():
    if AWS_PROFILE:
        return boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION,
        )
    return boto3.Session(region_name=AWS_REGION)


def embed_text(text: str) -> list[float]:
    client = _session().client("bedrock-runtime")

    body = json.dumps(
        {
            "inputText": text,
            "dimensions": EMBEDDING_DIMENSIONS,
            "normalize": True,
        }
    )

    response = client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=body,
        accept="application/json",
        contentType="application/json",
    )

    payload = json.loads(response["body"].read())
    embedding = payload["embedding"]

    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise RuntimeError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, got {len(embedding)}"
        )

    return embedding


def runbook_embedding_text(runbook) -> str:
    keywords = ", ".join(runbook.keywords or [])
    return (
        f"Runbook title: {runbook.title}\n"
        f"Problem type: {runbook.problem_type}\n"
        f"Description: {runbook.description}\n"
        f"Keywords: {keywords}\n"
        f"Troubleshooting steps:\n{runbook.content}"
    )

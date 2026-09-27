import os

import httpx
import pytest


BASE_URL = os.getenv("OPSPILOT_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "healthy"
    assert body["database"] == "connected"


def test_services_endpoint(client):
    response = client.get("/services")
    assert response.status_code == 200

    services = response.json()
    assert isinstance(services, list)


def test_incidents_endpoint(client):
    response = client.get("/incidents")
    assert response.status_code == 200

    incidents = response.json()
    assert isinstance(incidents, list)

    if incidents:
        required = {
            "id",
            "service_id",
            "title",
            "severity",
            "status",
            "summary",
            "evidence",
        }
        assert required.issubset(incidents[0].keys())


def test_runbooks_endpoint(client):
    response = client.get("/runbooks")
    assert response.status_code == 200

    runbooks = response.json()
    assert isinstance(runbooks, list)

    if runbooks:
        required = {
            "id",
            "title",
            "problem_type",
            "description",
            "keywords",
            "content",
        }
        assert required.issubset(runbooks[0].keys())


def test_incident_1001_if_present(client):
    incidents = client.get("/incidents").json()

    if not any(item["id"] == 1001 for item in incidents):
        pytest.skip("Incident 1001 is not present in this environment.")

    response = client.get("/incidents/1001")
    assert response.status_code == 200

    incident = response.json()
    assert incident["id"] == 1001
    assert incident["title"]


def test_recommended_runbook_if_incident_present(client):
    incidents = client.get("/incidents").json()

    if not any(item["id"] == 1001 for item in incidents):
        pytest.skip("Incident 1001 is not present in this environment.")

    response = client.get("/incidents/1001/recommended-runbook")

    # Semantic retrieval may legitimately return no result if no runbook
    # clears the configured similarity threshold.
    assert response.status_code in {200, 404}

    if response.status_code == 200:
        runbook = response.json()
        assert runbook["title"]
        assert runbook["content"]


def test_latest_analysis_endpoint_is_safe(client):
    incidents = client.get("/incidents").json()

    if not any(item["id"] == 1001 for item in incidents):
        pytest.skip("Incident 1001 is not present in this environment.")

    response = client.get("/incidents/1001/analysis/latest")

    # 404 is acceptable if no analysis has been generated yet.
    assert response.status_code in {200, 404}

    if response.status_code == 200:
        analysis = response.json()
        assert analysis["incident_id"] == 1001
        assert analysis["model_id"]
        assert isinstance(analysis["recommended_actions"], list)

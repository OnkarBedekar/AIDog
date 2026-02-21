"""Tests for API endpoints — health, auth, incidents, home."""
import pytest


class TestHealth:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "env" in data

    def test_health_no_auth_required(self, client):
        # Health check must be publicly accessible
        resp = client.get("/health")
        assert resp.status_code != 401


class TestAuth:
    def test_signup_creates_user(self, client):
        resp = client.post(
            "/api/auth/signup",
            json={"email": "new@example.com", "password": "password123", "role": "Backend"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["token"] != ""
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["role"] == "Backend"

    def test_signup_duplicate_email_fails(self, client):
        payload = {"email": "dup@example.com", "password": "pass123", "role": "SRE"}
        client.post("/api/auth/signup", json=payload)
        resp = client.post("/api/auth/signup", json=payload)
        assert resp.status_code == 400

    def test_login_valid_credentials(self, client):
        client.post(
            "/api/auth/signup",
            json={"email": "login@example.com", "password": "mypassword", "role": "ML"},
        )
        resp = client.post(
            "/api/auth/login",
            json={"email": "login@example.com", "password": "mypassword"},
        )
        assert resp.status_code == 200
        assert "token" in resp.json()

    def test_login_wrong_password_fails(self, client):
        client.post(
            "/api/auth/signup",
            json={"email": "wrongpw@example.com", "password": "correct", "role": "SRE"},
        )
        resp = client.post(
            "/api/auth/login",
            json={"email": "wrongpw@example.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_login_unknown_user_fails(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "whatever"},
        )
        assert resp.status_code == 401

    def test_get_me_authenticated(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "user" in data
        assert "@example.com" in data["user"]["email"]  # unique per-test email

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code in (401, 403)

    def test_token_is_jwt_format(self, client):
        resp = client.post(
            "/api/auth/signup",
            json={"email": "jwt@example.com", "password": "pass1234", "role": "SRE"},
        )
        token = resp.json()["token"]
        parts = token.split(".")
        assert len(parts) == 3, "JWT must have 3 dot-separated parts"


class TestIncidents:
    def test_list_incidents_requires_auth(self, client):
        resp = client.get("/api/incidents")
        assert resp.status_code in (401, 403)

    def test_list_incidents_returns_list(self, client, auth_headers):
        resp = client.get("/api/incidents", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_incident_not_found(self, client, auth_headers):
        resp = client.get("/api/incidents/999999", headers=auth_headers)
        assert resp.status_code == 404

    def test_create_incident_from_monitor(self, client, auth_headers):
        resp = client.post(
            "/api/incidents/from-monitor",
            params={"monitor_id": "test_monitor_001"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data["monitor_id"] == "test_monitor_001"
        assert data["state"] in ("open", "investigating")

    def test_create_incident_from_monitor_idempotent(self, client, auth_headers):
        """Creating from same monitor_id twice returns the same incident."""
        r1 = client.post(
            "/api/incidents/from-monitor",
            params={"monitor_id": "idem_monitor"},
            headers=auth_headers,
        )
        r2 = client.post(
            "/api/incidents/from-monitor",
            params={"monitor_id": "idem_monitor"},
            headers=auth_headers,
        )
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["id"] == r2.json()["id"]

    def test_list_incidents_after_create(self, client, auth_headers):
        client.post(
            "/api/incidents/from-monitor",
            params={"monitor_id": "list_test_monitor"},
            headers=auth_headers,
        )
        resp = client.get("/api/incidents", headers=auth_headers)
        assert resp.status_code == 200
        incidents = resp.json()
        assert len(incidents) >= 1

    def test_execute_step_requires_auth(self, client):
        resp = client.post("/api/incidents/1/steps/execute", json={"step_id": "step_1"})
        assert resp.status_code in (401, 403)

    def test_execute_step_on_nonexistent_incident(self, client, auth_headers):
        resp = client.post(
            "/api/incidents/999999/steps/execute",
            json={"step_id": "step_1"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_execute_step_returns_result(self, client, auth_headers):
        # Create an incident first
        inc_resp = client.post(
            "/api/incidents/from-monitor",
            params={"monitor_id": "step_exec_monitor"},
            headers=auth_headers,
        )
        incident_id = inc_resp.json()["id"]

        resp = client.post(
            f"/api/incidents/{incident_id}/steps/execute",
            json={"step_id": "step_abc"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["step_id"] == "step_abc"
        assert data["result"]["status"] == "completed"
        assert "updated_investigation_graph" in data


class TestHomeOverview:
    def test_overview_requires_auth(self, client):
        resp = client.get("/api/home/overview")
        assert resp.status_code in (401, 403)

    def test_overview_returns_expected_keys(self, client, auth_headers):
        resp = client.get("/api/home/overview", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "servicesYouTouch" in data
        assert "topEndpoints" in data
        assert "liveChartsData" in data
        assert "activeAlerts" in data
        assert "recentIncidents" in data
        assert "learnedPatterns" in data
        assert "suggestedImprovements" in data

    def test_overview_types(self, client, auth_headers):
        resp = client.get("/api/home/overview", headers=auth_headers)
        data = resp.json()
        assert isinstance(data["servicesYouTouch"], list)
        assert isinstance(data["topEndpoints"], list)
        assert isinstance(data["liveChartsData"], dict)
        assert isinstance(data["activeAlerts"], list)
        assert isinstance(data["recentIncidents"], list)
        assert isinstance(data["learnedPatterns"], list)
        assert isinstance(data["suggestedImprovements"], list)

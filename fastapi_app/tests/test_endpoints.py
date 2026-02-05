"""
Tests for FastAPI endpoints.
"""

from fastapi import status


class TestListAllEndpoint:
    """Tests for /listall endpoint."""

    def test_listall_success(self, client):
        """Test successful list all models."""
        response = client.get("/listall")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR]

    def test_listall_returns_json(self, client):
        """Test that /listall returns JSON response."""
        response = client.get("/listall")
        assert response.headers["content-type"].startswith("application/json")


class TestEvaluateEndpoint:
    """Tests for /evaluate endpoint."""

    def test_evaluate_missing_authorization(
            self, client, sample_evaluate_data):
        """Test evaluate without authorization header."""
        # Remove authorization header
        del sample_evaluate_data["authorization"]
        response = client.post("/evaluate", data=sample_evaluate_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_evaluate_missing_task_id(self, client, sample_evaluate_data):
        """Test evaluate without task_id."""
        del sample_evaluate_data["task_id"]
        response = client.post("/evaluate", data=sample_evaluate_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_evaluate_invalid_theme(self, client, sample_evaluate_data):
        """Test evaluate with empty theme."""
        sample_evaluate_data["theme"] = ""
        response = client.post("/evaluate", data=sample_evaluate_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_evaluate_invalid_prog_lang(self, client, sample_evaluate_data):
        """Test evaluate with invalid programming language."""
        sample_evaluate_data["prog_lang"] = ""
        response = client.post("/evaluate", data=sample_evaluate_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPopulateRagEndpoint:
    """Tests for /examples/populate endpoint."""

    def test_populate_rag_missing_theme(self, client):
        """Test populate RAG without theme."""
        response = client.post("/examples/populate", json={"examples": []})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_populate_rag_invalid_examples(self, client):
        """Test populate RAG with invalid examples."""
        response = client.post(
            "/examples/populate",
            json={"theme": "python", "examples": "invalid"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteRagEndpoint:
    """Tests for /examples/delete endpoint."""

    def test_delete_example_missing_task_id(self, client):
        """Test delete without task_id."""
        response = client.post(
            "/examples/delete",
            data={"theme": "python", "prog_lang": "python"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_example_invalid_task_id(self, client):
        """Test delete with invalid task_id."""
        response = client.post(
            "/examples/delete",
            data={"task_id": -1, "theme": "python", "prog_lang": "python"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_example_invalid_prog_lang(self, client):
        """Test delete with invalid programming language."""
        response = client.post(
            "/examples/delete",
            data={"task_id": 1, "theme": "python", "prog_lang": "invalid_lang"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestHealthCheckEndpoint:
    """Tests for /health endpoint."""

    def test_health_check_returns_healthy(self, client):
        """Test that health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"

    def test_health_check_includes_version(self, client):
        """Test that health check includes version."""
        response = client.get("/health")
        assert "version" in response.json()

    def test_health_check_returns_json(self, client):
        """Test that health check returns JSON response."""
        response = client.get("/health")
        assert response.headers["content-type"].startswith("application/json")

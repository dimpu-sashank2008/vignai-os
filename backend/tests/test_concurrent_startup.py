"""
VIGNAI OS — Multi-Worker Concurrent Database Startup Regression Test Suite
Validates that concurrent workers starting up simultaneously do not encounter
duplicate-object or duplicate-type race condition errors (e.g. pg_type_typname_nsp_index).
"""
import concurrent.futures
import pytest
from app.database import (
    engine,
    verify_database_schema,
    safe_initialize_database,
    check_database_connection,
)
from app.main import app
from fastapi.testclient import TestClient


def test_database_connectivity_ping():
    """Ensure database connection ping helper functions correctly."""
    assert check_database_connection() is True


def test_verify_database_schema_returns_bool():
    """Ensure schema verification returns boolean without raising DDL exceptions."""
    is_valid = verify_database_schema()
    assert isinstance(is_valid, bool)


def test_concurrent_schema_initialization_race_condition():
    """
    Simulate multiple concurrent Uvicorn workers booting up simultaneously
    and executing safe_initialize_database() in parallel threads.
    Guarantees no race condition or duplicate object errors occur.
    """
    worker_count = 5
    errors = []

    def simulate_worker(worker_id: int):
        try:
            safe_initialize_database()
            return f"worker-{worker_id}-success"
        except Exception as exc:
            errors.append((worker_id, exc))
            raise

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(simulate_worker, i) for i in range(worker_count)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(errors) == 0, f"Errors encountered during concurrent worker initialization: {errors}"
    assert len(results) == worker_count
    assert verify_database_schema() is True


def test_lifespan_startup_skips_redundant_ddl(client=None):
    """
    Verify that when tables already exist, lifespan startup checks schema
    and skips redundant DDL without throwing UniqueViolation errors.
    """
    with TestClient(app) as test_client:
        res = test_client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["database"] == "CONNECTED"

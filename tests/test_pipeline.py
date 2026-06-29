# tests/test_pipeline.py
import os
import sys
import sqlite3
import pytest
from pydantic import ValidationError

# Ensure the pipeline directory can be found by Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data_pipeline')))

from models import FinancialLogInput
from ingest import IngestionPipeline


# ==========================================
# FIXTURES (Setup and Teardown)
# ==========================================
@pytest.fixture
def test_db_path():
    """Creates a temporary database file for isolated integration testing."""
    db_path = "test_platform_isolated.db"

    # Initialize schema on the temporary file
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE financial_compliance_logs (
            id TEXT PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            log_level TEXT NOT NULL,
            masked_account TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            raw_payload_json TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

    yield db_path  # Provide the file path to the test case

    # Clean up and delete the test database file after the test finishes
    if os.path.exists(db_path):
        os.remove(db_path)


# ==========================================
# UNIT TESTS (Pydantic Validation & Masking)
# ==========================================
def test_valid_financial_log_input():
    payload = {
        "account_number": "123456789012",
        "amount": 5000.00,
        "currency": "NOK",
        "log_level": "CRITICAL"
    }
    model = FinancialLogInput(**payload)
    assert model.currency == "NOK"
    assert model.log_level == "CRITICAL"


def test_invalid_log_level_raises_error():
    payload = {
        "account_number": "123456789012",
        "amount": 5000.00,
        "currency": "NOK",
        "log_level": "INVALID_LEVEL"
    }
    with pytest.raises(ValidationError):
        FinancialLogInput(**payload)


def test_account_number_masking():
    payload = {
        "account_number": "987654321098",
        "amount": 100.0,
        "currency": "EUR"
    }
    model = FinancialLogInput(**payload)
    assert model.get_masked_account() == "********1098"


# ==========================================
# INTEGRATION TESTS (Pipeline Execution)
# ==========================================
def test_pipeline_ingestion_and_resiliency(test_db_path):
    """Tests full end-to-end ingestion processing using an isolated file DB."""
    pipeline = IngestionPipeline(db_path=test_db_path)

    mixed_mock_stream = [
        {"account_number": "111122223333", "amount": 2500.0, "currency": "NOK", "log_level": "INFO"},
        {"account_number": "BAD_ACC", "amount": 0.0, "currency": "USD"},  # Malformed
        {"account_number": "444455556666", "amount": -12.50, "currency": "EUR", "log_level": "WARNING"}
    ]

    # This automatically opens, writes, and closes its own connections cleanly
    pipeline.process_and_load(mixed_mock_stream)

    # Open a completely fresh connection to confirm changes were safely committed
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT masked_account, amount, log_level FROM financial_compliance_logs ORDER BY amount DESC")
    rows = cursor.fetchall()
    conn.close()

    # Verification assertions
    assert len(rows) == 2

    assert rows[0][0] == "********3333"
    assert rows[0][1] == 2500.0
    assert rows[0][2] == "INFO"

    assert rows[1][0] == "********6666"
    assert rows[1][1] == -12.50
    assert rows[1][2] == "WARNING"

# data_pipeline/ingest.py
import sqlite3
import json
from datetime import datetime, timezone
import uuid
from typing import List, Dict, Any
from models import FinancialLogInput

class IngestionPipeline:
    def __init__(self, db_path: str = "platform_data.db"):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def process_and_load(self, raw_records: List[Dict[str, Any]]):
        """Validates, masks, and batch-inserts data into the database."""
        validated_rows = []

        for record in raw_records:
            try:
                # Pass data through Pydantic validation gate
                validated_data = FinancialLogInput(**record)

                # Format payload for database injection using timezone-aware UTC standard
                row = (
                    str(uuid.uuid4()),
                    datetime.now(timezone.utc).isoformat(),
                    validated_data.log_level,
                    validated_data.get_masked_account(),
                    validated_data.amount,
                    validated_data.currency.upper(),
                    json.dumps(record)
                )
                validated_rows.append(row)
            except Exception as e:
                print(f"Data Validation Dropped Record: {record}. Error: {e}")
                continue

        if validated_rows:
            query = """
                INSERT INTO financial_compliance_logs
                (id, timestamp, log_level, masked_account, amount, currency, raw_payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.executemany(query, validated_rows)
                conn.commit()
                print(f"Successfully ingested {len(validated_rows)} records.")
            except sqlite3.Error as db_err:
                print(f"Database transaction aborted: {db_err}")
                conn.rollback()
            finally:
                conn.close()

if __name__ == "__main__":
    mock_stream = [
        {"account_number": "123456789012", "amount": 15000.50, "currency": "NOK", "log_level": "INFO"},
        {"account_number": "987654321098", "amount": -450.00, "currency": "EUR", "log_level": "CRITICAL"},
        {"account_number": "SHORT", "amount": 0.0, "currency": "USD"}
    ]

    pipeline = IngestionPipeline()
    pipeline.process_and_load(mock_stream)

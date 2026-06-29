-- schema.sql
-- Drop table if exists to ensure reproducibility in container environments
DROP TABLE IF EXISTS financial_compliance_logs;

CREATE TABLE financial_compliance_logs (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    log_level TEXT NOT NULL,
    masked_account TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    raw_payload_json TEXT NOT NULL
);

-- Index critical columns to optimize search queries and platform performance
CREATE INDEX idx_logs_timestamp ON financial_compliance_logs(timestamp);
CREATE INDEX idx_logs_level ON financial_compliance_logs(log_level);

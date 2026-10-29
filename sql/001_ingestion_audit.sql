CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(100) PRIMARY KEY,
    applied_at DATETIME(6) NOT NULL
);

CREATE TABLE IF NOT EXISTS source_documents (
    source_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    source_url TEXT NULL,
    reporting_period VARCHAR(100) NULL,
    content_sha256 CHAR(64) NOT NULL,
    ingested_at DATETIME(6) NOT NULL,
    status VARCHAR(30) NOT NULL,
    PRIMARY KEY (source_id),
    UNIQUE KEY uq_source_documents_file_hash (filename, content_sha256)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    run_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    source_id BIGINT UNSIGNED NOT NULL,
    started_at DATETIME(6) NOT NULL,
    completed_at DATETIME(6) NULL,
    status VARCHAR(30) NOT NULL,
    records_processed INT UNSIGNED NOT NULL DEFAULT 0,
    records_accepted INT UNSIGNED NOT NULL DEFAULT 0,
    records_rejected INT UNSIGNED NOT NULL DEFAULT 0,
    records_duplicate INT UNSIGNED NOT NULL DEFAULT 0,
    records_failed INT UNSIGNED NOT NULL DEFAULT 0,
    error_details JSON NULL,
    PRIMARY KEY (run_id),
    KEY idx_ingestion_runs_source_id (source_id),
    CONSTRAINT fk_ingestion_runs_source
        FOREIGN KEY (source_id) REFERENCES source_documents(source_id)
);

CREATE TABLE IF NOT EXISTS rejected_records (
    rejection_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    run_id BIGINT UNSIGNED NOT NULL,
    record_index INT UNSIGNED NOT NULL,
    source_unique_id VARCHAR(100) NULL,
    original_record JSON NOT NULL,
    validation_errors JSON NOT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (rejection_id),
    KEY idx_rejected_records_run_id (run_id),
    CONSTRAINT fk_rejected_records_run
        FOREIGN KEY (run_id) REFERENCES ingestion_runs(run_id)
);

ALTER TABLE outbreaks
    ADD COLUMN source_id BIGINT UNSIGNED NULL,
    ADD COLUMN ingestion_run_id BIGINT UNSIGNED NULL,
    ADD KEY idx_outbreaks_source_id (source_id),
    ADD KEY idx_outbreaks_ingestion_run_id (ingestion_run_id),
    ADD CONSTRAINT fk_outbreaks_source
        FOREIGN KEY (source_id) REFERENCES source_documents(source_id),
    ADD CONSTRAINT fk_outbreaks_ingestion_run
        FOREIGN KEY (ingestion_run_id) REFERENCES ingestion_runs(run_id);

INSERT INTO schema_migrations (version, applied_at)
VALUES ('001_ingestion_audit', UTC_TIMESTAMP(6));

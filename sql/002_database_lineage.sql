CREATE TABLE IF NOT EXISTS data_quality_issues (
    issue_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    record_id BIGINT UNSIGNED NULL,
    run_id BIGINT UNSIGNED NULL,
    source_unique_id VARCHAR(100) NULL,
    issue_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    original_value JSON NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    detected_at DATETIME(6) NOT NULL,
    PRIMARY KEY (issue_id),
    KEY idx_data_quality_issues_record_id (record_id),
    KEY idx_data_quality_issues_run_id (run_id),
    KEY idx_data_quality_issues_status (status),
    CONSTRAINT fk_data_quality_issues_record
        FOREIGN KEY (record_id) REFERENCES outbreaks(record_id),
    CONSTRAINT fk_data_quality_issues_run
        FOREIGN KEY (run_id) REFERENCES ingestion_runs(run_id),
    CONSTRAINT chk_data_quality_issue_reference
        CHECK (record_id IS NOT NULL OR run_id IS NOT NULL)
);

ALTER TABLE outbreaks
    ADD KEY idx_outbreaks_disease (disease),
    ADD KEY idx_outbreaks_state (state),
    ADD KEY idx_outbreaks_district (district(100)),
    ADD KEY idx_outbreaks_reporting_date (reporting_date),
    ADD KEY idx_outbreaks_status (status);

INSERT INTO schema_migrations (version, applied_at)
VALUES ('002_database_lineage', UTC_TIMESTAMP(6));

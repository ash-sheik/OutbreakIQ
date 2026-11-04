
-- OutbreakIQ Module 04: Anomaly Alerts
-- Review this migration before executing in MySQL Workbench.

CREATE TABLE IF NOT EXISTS anomaly_alerts (
    alert_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    rule_id VARCHAR(100) NOT NULL,
    rule_version INT UNSIGNED NOT NULL,
    disease VARCHAR(150) NOT NULL,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(255) NOT NULL,
    reporting_period_start DATE NOT NULL,
    reporting_period_end DATE NOT NULL,
    observed_value DECIMAL(18, 4) NOT NULL,
    baseline_value DECIMAL(18, 4) NOT NULL,
    absolute_change DECIMAL(18, 4) NOT NULL,
    percentage_change DECIMAL(12, 4) NULL,
    score DECIMAL(12, 4) NULL,
    threshold DECIMAL(12, 4) NOT NULL,
    history_periods INT UNSIGNED NOT NULL,
    analysis_run_key CHAR(64) NOT NULL,
    interpretation VARCHAR(255) NOT NULL DEFAULT
        'Analytical finding requiring verification',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    PRIMARY KEY (alert_id),

    UNIQUE KEY uq_anomaly_alert_observation (
        rule_id,
        rule_version,
        disease,
        state,
        district,
        reporting_period_start,
        reporting_period_end
    ),

    KEY idx_anomaly_alert_period (
        reporting_period_start,
        reporting_period_end
    ),

    KEY idx_anomaly_alert_location (
        state,
        disease
    )
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS anomaly_alert_evidence (
    evidence_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    alert_id BIGINT UNSIGNED NOT NULL,
    record_id BIGINT UNSIGNED NULL,
    evidence_type VARCHAR(50) NOT NULL,
    evidence_description TEXT NOT NULL,
    evidence_key CHAR(64) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    PRIMARY KEY (evidence_id),

    UNIQUE KEY uq_alert_evidence_fingerprint (
        alert_id,
        evidence_key
    ),

    KEY idx_alert_evidence_record (record_id),

    CONSTRAINT fk_alert_evidence_alert
        FOREIGN KEY (alert_id)
        REFERENCES anomaly_alerts (alert_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_alert_evidence_outbreak
        FOREIGN KEY (record_id)
        REFERENCES outbreaks (record_id)
        ON DELETE RESTRICT
) ENGINE=InnoDB;

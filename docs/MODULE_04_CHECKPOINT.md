# OutbreakIQ – Module 04 Implementation Checkpoint

**Module:** Anomaly Detection & Alert Management
**Status:** Implemented, tested and pushed to GitHub
**Commit:** `00d511a`
**Branch:** `master`
**Date:** 4 November 2026

## 1. Implementation Summary

Module 04 introduces deterministic, explainable anomaly detection into OutbreakIQ.

The module evaluates weekly disease observations against historical baselines, identifies unusual increases, stores alerts in MySQL, and exposes the results through FastAPI.

An anomaly is an analytical finding requiring verification. It does not confirm an outbreak.

## 2. Architecture

The processing workflow is:

1. Retrieve weekly observations from MySQL.
2. Calculate historical baselines using previous observations.
3. Evaluate observations against the configured anomaly rule.
4. Generate explainable anomaly alerts.
5. Persist alerts and supporting evidence in MySQL.
6. Return the analysis results through FastAPI.

### Main implementation files

| File | Responsibility |
|---|---|
| `app/analytics/anomaly_rules.py` | Deterministic anomaly evaluation |
| `app/analytics/anomaly_service.py` | Analysis orchestration and alert generation |
| `app/repositories/anomaly_alert_repository.py` | Alert and evidence persistence |
| `app/main.py` | Anomaly and alert API endpoints |
| `sql/003_anomaly_alerts.sql` | Alert and evidence database schema |

## 3. Anomaly Detection Methodology

**Rule:** `case_increase_v1`
**Rule version:** 1
**Default percentage increase threshold:** 50%
**Minimum historical observations:** 4
**Historical lookback:** 8 available observations

Percentage change:

`((Observed Cases - Historical Baseline) / Historical Baseline) × 100`

The historical baseline is calculated using the arithmetic mean of previous available weekly observations.

The current observation is excluded from its own baseline.

When the historical baseline is zero, percentage change is undefined and the rule does not generate an increase alert.

The current implementation uses previous available observations, not necessarily consecutive calendar weeks.

## 4. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/analysis/run` | Execute anomaly analysis |
| GET | `/alerts` | Retrieve alerts with filters and pagination |
| GET | `/alerts/{alert_id}` | Retrieve an alert and its evidence |

## 5. Database Changes

Migration: `sql/003_anomaly_alerts.sql`

Tables introduced:

- `anomaly_alerts`
- `anomaly_alert_evidence`

The implementation includes:

- Unique alert observation constraints.
- Evidence fingerprinting.
- Foreign-key relationships.
- Transaction-based persistence.
- Duplicate prevention during repeated analysis.

## 6. Verification Results

### Automated testing

**52 tests passed, 1 non-blocking deprecation warning.**

### Real MySQL integration

Verified:

- Alert insertion.
- Evidence insertion.
- Alert retrieval.
- Evidence retrieval.
- Duplicate alert prevention.
- Duplicate evidence prevention.
- Alert listing.
- Cleanup of temporary integration-test records.

### Real-data analysis

Test dataset: Acute Diarrheal Disease, Odisha, Balangir.

- Weekly observations evaluated: 16.
- Alerts detected: 5.
- Alerts matched independent manual calculations.
- Repeated analysis returned the same alert IDs.
- Evidence counts remained unchanged after repeated execution.

### GitHub deployment

Repository: `https://github.com/ash-sheik/OutbreakIQ`

Commit: `00d511a – Add anomaly detection and alert persistence`

Branch: `master`

Status: Module 04 implementation successfully pushed to origin/master in commit 00d511a.

## 7. Known Limitations and Future Improvements

1. Historical baselines use available observations rather than requiring consecutive calendar weeks.
2. Disease and location names contain inconsistencies that may split equivalent groups.
3. Sparse reporting and missing weeks can affect interpretation.
4. The current anomaly rule uses a percentage-increase threshold; it is not a seasonal or advanced statistical model.
5. Source-level record traceability for aggregated weekly evidence requires further improvement.
6. Alert review and acknowledgement workflows are not yet implemented.

## 8. Next Development Milestone

**Stage 6 – Gemini Integration**

Planned capabilities:

- Retrieve an existing alert and its supporting evidence.
- Construct a structured evidence payload.
- Generate an investigation brief using Gemini.
- Validate numerical claims and alert references.
- Store the generated brief against its alert.
- Handle API failures without affecting existing alerts.

The AI-generated brief must explain verified analytical evidence and must not independently declare an outbreak.

---

**Checkpoint conclusion:** Module 04 has been implemented, tested against real MySQL data, verified for repeat-run idempotency, and published to GitHub.

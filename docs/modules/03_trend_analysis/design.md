# Trend analysis design

Create an analytics service that queries canonical records with reporting dates, groups them by ISO reporting week, and returns deterministic summaries. Define a baseline configuration with lookback-window size and minimum comparable periods.

Trend results initially remain request-time calculations. Anomaly detection receives a structured trend result containing observed value, baseline mean, supporting record IDs, and limitations.

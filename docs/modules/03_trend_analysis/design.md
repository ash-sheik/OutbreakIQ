# Trend analysis design

The analytics service queries canonical records with reporting dates, groups them by ISO reporting week, and returns deterministic summaries. Its default baseline is the preceding eight observed weeks for the same disease, state, and district; it requires at least four prior weeks before producing a baseline.

Trend results remain request-time calculations. They expose the supporting weekly observations and limitations, including excluded records with missing reporting dates. Anomaly detection receives the observed value, baseline mean, and evidence.

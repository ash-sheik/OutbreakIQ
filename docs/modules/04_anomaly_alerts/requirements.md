# Anomaly alert requirements

- Evaluate a versioned, explainable baseline rule against aggregated observations.
- Store observed value, baseline value, absolute change, percentage change when defined, score, threshold, comparison period, and timestamp.
- Do not calculate a finite percentage change when baseline is zero.
- Label every alert as an analytical finding requiring verification, never a confirmed outbreak.
- Link each alert to its evidence records and data-quality limitations.

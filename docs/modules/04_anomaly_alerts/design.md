# Anomaly alert design

Start with one rule version: a minimum number of historical periods plus a configurable percentage-change threshold. The rule emits no alert for insufficient history or zero baseline unless a separately documented rule is approved.

Persist alerts and their evidence references. An analysis run is idempotent for a given rule version, observation key, and reporting period.

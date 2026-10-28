# Ingestion audit design

Add a pipeline entry point that creates an ingestion run, registers a source document, extracts or loads records, validates them, saves accepted rows, stores rejected rows, and closes the run with a final status. PDF extraction returns rows plus page and table metadata; it does not overwrite the copied CSV source.

Use database transactions for run status updates and batch record saves. A failed extraction records its failure against the run and source document.

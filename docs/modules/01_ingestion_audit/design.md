# Ingestion audit design

The pipeline creates an ingestion run, registers a source document by filename and SHA-256 content hash, validates rows, saves accepted rows, stores rejected rows, and closes the run with a final status. PDF extraction returns rows plus page and table metadata; it does not overwrite the copied CSV source.

Use database transactions for run status updates and batch record saves. A failed extraction records its failure against the run and source document.

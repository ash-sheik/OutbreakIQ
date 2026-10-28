# API query design

Separate route handlers from repositories as the API expands. Query schemas define optional filters, date boundaries, limit, and offset. Repository functions use parameterized SQL and return total-count metadata with each page.

Use FastAPI exception handlers to return a common error envelope for request validation, missing records, and database failures.

# Database lineage tasks

- [x] Write an additive MySQL migration with rollback notes.
- [x] Apply `sql/002_database_lineage.sql` using a MySQL account with `CREATE` and `ALTER` privileges.
- [x] Add lineage columns to new records without changing historical source values.
- [x] Add source, run, and issue repositories.
- [x] Add indexes for planned filtered queries.
- [x] Document the migration and data-backfill policy: historical records retain nullable lineage fields; future imports create source and run links.
- [ ] Test foreign-key and uniqueness behavior.

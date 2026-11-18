# Consistent database backup and restore

The commands use SQLite's online backup API rather than copying a possibly changing database file. Backups contain account hashes and student records: keep them private, outside the public repository.

## Back up

```bash
python manage.py backup_database backups/campus-2026-11-18.sqlite3
```

Use a new filename every time. The command refuses to overwrite an existing destination and checks the resulting database's integrity. Download an additional private copy through your hosting account for recovery if the account's storage is lost.

## Restore and verify a separate instance

```bash
python manage.py restore_database backups/campus-2026-11-18.sqlite3 restored-campus.sqlite3
```

This creates a **new file** and never overwrites the live database. Test the copy in a separate local checkout/virtualenv by setting `DJANGO_DB_PATH` to its absolute path. Run migrations only if the code/database versions require it. Use the same source version first.

Compare user and event counts, each registration's status, per-event confirmed counts, waitlist order (`joined_at`, then ID), and attendance. The automated `test_TC025_backup_restore_exact_rows_and_no_overwrite` compares all rows of the relevant tables between the source and restored copy, and checks `PRAGMA integrity_check`.

For a real production recovery, stop/disable the affected Web app so no writes continue, retain the current database as a recovery copy, change the private `DJANGO_DB_PATH` to the verified restored file, and reload the application. Recheck login and registration from another browser. Never restore over a running database.

The local restore test has passed. Repeat this exercise against the final demonstration deployment before marking deployment recovery acceptance as complete.

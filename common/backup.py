"""SQLite online backup: consistent snapshot, never overwrite a destination."""
import sqlite3
from contextlib import closing
from pathlib import Path


def copy_database(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file():
        raise ValueError("Source database does not exist.")
    if source == destination or destination.exists():
        raise ValueError("Use a new destination file; existing files are never overwritten.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the path atomically to protect an existing backup.
    with destination.open("xb"):
        pass
    try:
        destination.chmod(0o600)
        # A SQLite connection's own context manager does not close it.
        # Close both handles before returning or removing an incomplete backup.
        with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as src:
            with closing(sqlite3.connect(destination)) as dst:
                with dst:
                    src.backup(dst)
                    if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("Database integrity check failed.")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return destination

"""Backup file handles must be released before returning or removing files."""
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from common.backup import copy_database


CONNECT = sqlite3.connect
UNLINK = Path.unlink


class IntegrityFailureConnection(sqlite3.Connection):
    def execute(self, sql, *args, **kwargs):
        if sql == "PRAGMA integrity_check":
            return Mock(fetchone=Mock(return_value=("injected integrity failure",)))
        return super().execute(sql, *args, **kwargs)


class BackupResourceTests(TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        # Keep references alive: garbage collection must not hide a missing close.
        self.opened = []
        self.addCleanup(self.close_tracked_connections)
        self.source = Path(self.folder.name) / "source.sqlite3"
        self.destination = Path(self.folder.name) / "backup.sqlite3"
        with closing(CONNECT(self.source)) as connection:
            with connection:
                connection.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, name TEXT)")
                connection.execute("INSERT INTO sample VALUES (1, 'campus event')")

    def close_tracked_connections(self):
        for connection in self.opened:
            connection.close()

    def track_connect(self, *args, **kwargs):
        connection = CONNECT(*args, **kwargs)
        self.opened.append(connection)
        return connection

    def assert_connections_closed(self):
        for connection in self.opened:
            with self.assertRaises(sqlite3.ProgrammingError):
                connection.execute("SELECT 1")

    def guard_unlink(self, path, *args, **kwargs):
        # Model Windows file locking on every platform, including Linux CI.
        for connection in self.opened:
            try:
                connection.in_transaction
            except sqlite3.ProgrammingError:
                continue
            raise PermissionError("Database connection is still open during cleanup.")
        return UNLINK(path, *args, **kwargs)

    def test_TC025_backup_closes_connections_before_return(self):
        with patch("common.backup.sqlite3.connect", side_effect=self.track_connect):
            result = copy_database(self.source, self.destination)
        self.assertEqual(result, self.destination)
        self.assertEqual(len(self.opened), 2)
        self.assert_connections_closed()
        with closing(CONNECT(result)) as connection:
            self.assertEqual(connection.execute("SELECT * FROM sample").fetchall(), [(1, "campus event")])
        result.unlink()
        self.assertFalse(result.exists())

    def test_TC025_failed_backup_closes_connections_before_cleanup(self):
        self.source.write_bytes(b"not a SQLite database")
        with patch("common.backup.sqlite3.connect", side_effect=self.track_connect):
            with patch.object(Path, "unlink", autospec=True, side_effect=self.guard_unlink):
                with self.assertRaises(sqlite3.DatabaseError):
                    copy_database(self.source, self.destination)
        self.assertEqual(len(self.opened), 2)
        self.assert_connections_closed()
        self.assertFalse(self.destination.exists())

    def test_TC025_destination_open_failure_closes_source(self):
        def fail_second_connect(*args, **kwargs):
            if self.opened:
                raise sqlite3.OperationalError("Injected destination open failure")
            return self.track_connect(*args, **kwargs)

        with patch("common.backup.sqlite3.connect", side_effect=fail_second_connect):
            with patch.object(Path, "unlink", autospec=True, side_effect=self.guard_unlink):
                with self.assertRaisesRegex(sqlite3.OperationalError, "Injected destination open failure"):
                    copy_database(self.source, self.destination)
        self.assertEqual(len(self.opened), 1)
        self.assert_connections_closed()
        self.assertFalse(self.destination.exists())

    def test_TC025_integrity_failure_closes_connections_before_cleanup(self):
        def fail_integrity_check(*args, **kwargs):
            return self.track_connect(*args, factory=IntegrityFailureConnection, **kwargs)

        with patch("common.backup.sqlite3.connect", side_effect=fail_integrity_check):
            with patch.object(Path, "unlink", autospec=True, side_effect=self.guard_unlink):
                with self.assertRaisesRegex(ValueError, "Database integrity check failed"):
                    copy_database(self.source, self.destination)
        self.assertEqual(len(self.opened), 2)
        self.assert_connections_closed()
        self.assertFalse(self.destination.exists())

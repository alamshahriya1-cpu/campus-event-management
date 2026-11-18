import sqlite3
import tempfile
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from django.test import TransactionTestCase, override_settings
from django.db import connections
from django.contrib.auth import get_user_model
from common.backup import copy_database
from common.errors import AppError
from events.models import Event
from events.services import create_event, publish_event, cancel_event
from registrations.models import Registration
from registrations.services import register, cancel_registration
from tests.test_application import make_user, event_fields


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class TransactionAcceptanceTests(TransactionTestCase):
    def setUp(self):
        self.organizer = make_user("organizer", "Organizer")
        self.students = [make_user("student"+str(i)) for i in range(5)]
        self.event = create_event(self.organizer, event_fields(capacity=1))
        publish_event(self.organizer, self.event.id)

    def compete(self, user_ids):
        barrier = threading.Barrier(len(user_ids))
        def worker(user_id):
            connections.close_all()
            try:
                user = get_user_model().objects.get(pk=user_id)
                barrier.wait(timeout=10)
                return register(user, self.event.id)[0].status
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=len(user_ids)) as pool:
            return list(pool.map(worker, user_ids))

    def test_TC021_competing_requests_for_last_seat(self):
        statuses = self.compete([s.id for s in self.students])
        self.assertEqual(statuses.count("Confirmed"), 1)
        self.assertEqual(statuses.count("Waitlisted"), 4)
        self.assertEqual(Registration.objects.filter(status="Confirmed").count(), 1)

    def test_TC021_concurrent_duplicate_requests(self):
        statuses = self.compete([self.students[0].id]*4)
        self.assertEqual(statuses, ["Confirmed"]*4)
        self.assertEqual(Registration.objects.count(), 1)

    def test_TC021_registration_persists_after_connection_restart(self):
        reg, _ = register(self.students[0], self.event.id)
        connections.close_all()
        self.assertEqual(Registration.objects.get(pk=reg.id).status, "Confirmed")

    def test_TC021_event_cancellation_rolls_back_on_update_failure(self):
        for s in self.students[:2]: register(s, self.event.id)
        from django.db.models.query import QuerySet
        real_update = QuerySet.update
        def failing_update(query, **changes):
            if query.model is Registration:
                raise RuntimeError("Injected registration update failure")
            return real_update(query, **changes)
        with patch.object(QuerySet, "update", failing_update):
            with self.assertRaises(RuntimeError): cancel_event(self.organizer, self.event.id, "Test")
        self.assertEqual(Event.objects.get(pk=self.event.id).status, "Published")
        self.assertEqual(Registration.objects.filter(status="Confirmed").count(), 1)
        self.assertEqual(Registration.objects.filter(status="Waitlisted").count(), 1)

    def test_TC025_backup_restore_exact_rows_and_no_overwrite(self):
        for s in self.students: register(s, self.event.id)
        first = Registration.objects.get(student=self.students[0])
        cancel_registration(self.students[0], first.id)
        source = connections["default"].settings_dict["NAME"]
        with tempfile.TemporaryDirectory() as folder:
            backup = copy_database(source, Path(folder)/"backup.sqlite3")
            restored = copy_database(backup, Path(folder)/"restored.sqlite3")
            with sqlite3.connect(source) as original, sqlite3.connect(restored) as restored_conn:
                for table in ["auth_user", "auth_user_groups", "accounts_studentprofile", "events_event", "registrations_registration"]:
                    self.assertEqual(original.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall(), restored_conn.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall())
                self.assertEqual(restored_conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            with self.assertRaises(ValueError): copy_database(source, backup)

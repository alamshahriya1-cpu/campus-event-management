"""Account lifecycle helpers for the project's database-backed sessions."""
from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.models import Session
from django.utils import timezone


def deletion_blockers(student):
    """Keep every registration and event/attendance audit reference intact."""
    relations = (
        (student.registrations, "Event registrations, including cancelled registrations and past events"),
        (student.attendance_updates, "Attendance records updated by this account"),
        (student.created_events, "Events created by this account"),
        (student.cancelled_events, "Events cancelled by this account"),
    )
    return [label for records, label in relations if records.exists()]


def expire_student_sessions(student):
    """Remove this user's unexpired DB sessions inside the account transaction.

    The project uses Django's database session backend. Decode signed sessions
    instead of searching encoded data, and leave other users' sessions intact.
    Purging on either access-state transition also prevents stored old cookies
    from becoming valid again when an account is reactivated.
    """
    keys = [
        session.session_key
        for session in Session.objects.filter(expire_date__gt=timezone.now()).iterator()
        if str(session.get_decoded().get(SESSION_KEY)) == str(student.pk)
    ]
    if keys:
        Session.objects.filter(session_key__in=keys).delete()

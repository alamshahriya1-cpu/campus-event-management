"""Atomic seat allocation, FIFO promotion and attendance. FR009–FR016."""
from django.db import transaction
from django.http import Http404
from django.utils import timezone
from accounts.permissions import require_role
from common.errors import AppError, conflict
from events.models import Event
from events.services import lock_event
from .models import Registration


def check_open(event, now):
    if event.status != Event.Status.PUBLISHED or now >= event.registration_closes_at:
        raise conflict("Registration and student cancellation are closed for this event.")


@transaction.atomic
def register(actor, event_id):
    require_role(actor, ("Student",))
    event = lock_event(event_id)
    now = timezone.now()
    check_open(event, now)
    existing = event.registrations.filter(student=actor).first()
    if existing and existing.status != Registration.Status.CANCELLED:
        return existing, False
    has_seat = event.registrations.filter(status=Registration.Status.CONFIRMED).count() < event.capacity
    older_waiter = event.registrations.filter(status=Registration.Status.WAITLISTED).exists()
    status = Registration.Status.CONFIRMED if has_seat and not older_waiter else Registration.Status.WAITLISTED
    reg = existing or Registration(event=event, student=actor)
    reg.status, reg.joined_at = status, now
    reg.confirmed_at = now if status == Registration.Status.CONFIRMED else None
    reg.cancelled_at = reg.cancellation_source = None
    reg.attended = False
    reg.attendance_updated_at = reg.attendance_updated_by = None
    reg.save()
    return reg, existing is None


def promote_next(event, now):
    waiter = event.registrations.filter(status=Registration.Status.WAITLISTED).order_by("joined_at", "id").first()
    if waiter:
        waiter.status, waiter.confirmed_at = Registration.Status.CONFIRMED, now
        waiter.save(update_fields=["status", "confirmed_at"])


@transaction.atomic
def cancel_registration(actor, registration_id):
    require_role(actor, ("Student",))
    # Owner-scoped lookup returns 404 for another student's identifier.
    event_id = Registration.objects.filter(pk=registration_id, student=actor).values_list("event_id", flat=True).first()
    if event_id is None:
        raise Http404
    event = lock_event(event_id)
    reg = Registration.objects.get(pk=registration_id, student=actor)
    now = timezone.now()
    check_open(event, now)
    if reg.status == Registration.Status.CANCELLED:
        return reg
    was_confirmed = reg.status == Registration.Status.CONFIRMED
    reg.status, reg.cancelled_at, reg.cancellation_source = Registration.Status.CANCELLED, now, "Student"
    reg.attended = False
    reg.save(update_fields=["status", "cancelled_at", "cancellation_source", "attended"])
    if was_confirmed:
        promote_next(event, now)
    return reg


@transaction.atomic
def mark_attendance(actor, registration_id, attended):
    require_role(actor, ("Organizer",))
    if type(attended) is not bool:
        raise AppError("Attendance must be true or false.")
    event_id = Registration.objects.filter(pk=registration_id).values_list("event_id", flat=True).first()
    if event_id is None:
        raise Http404
    event = lock_event(event_id)
    reg = Registration.objects.get(pk=registration_id)
    now = timezone.now()
    if event.status == Event.Status.CANCELLED or now < event.start_at or reg.status != Registration.Status.CONFIRMED:
        raise conflict("Attendance is available from the event start, for confirmed participants only.")
    reg.attended, reg.attendance_updated_at, reg.attendance_updated_by = attended, now, actor
    reg.save(update_fields=["attended", "attendance_updated_at", "attendance_updated_by"])
    return reg

"""Event mutations. State and time are always checked inside the transaction."""
from django.db import transaction
from django.db.models import F
from django.http import Http404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from accounts.permissions import require_role
from common.errors import AppError, conflict
from .models import Event

TEXT_FIELDS = {"title": 120, "description": 2000, "category": 60, "venue": 120}
TIME_FIELDS = ("start_at", "end_at", "registration_closes_at")
EDIT_FIELDS = (*TEXT_FIELDS, *TIME_FIELDS, "capacity")


def lock_event(event_id):
    # A first write serializes SQLite writers; never assume row-level locking.
    if not Event.objects.filter(pk=event_id).update(allocation_version=F("allocation_version") + 1):
        raise Http404
    return Event.objects.get(pk=event_id)


def validate_fields(data, partial=False):
    if set(data) - set(EDIT_FIELDS):
        raise AppError("Only event fields can be changed.")
    if not partial and set(EDIT_FIELDS) - set(data):
        raise AppError("Complete all required event fields.")
    cleaned = {}
    for key, value in data.items():
        if key in TEXT_FIELDS:
            if not isinstance(value, str) or not value.strip() or len(value.strip()) > TEXT_FIELDS[key]:
                raise AppError(f"{key.replace('_', ' ').capitalize()} is required and must be at most {TEXT_FIELDS[key]} characters.")
            cleaned[key] = value.strip()
        elif key == "capacity":
            if type(value) is not int or not 1 <= value <= 200:
                raise AppError("Capacity must be a whole number between 1 and 200.")
            cleaned[key] = value
        else:
            try:
                dt = parse_datetime(value) if isinstance(value, str) else None
            except ValueError:
                dt = None
            if dt is None or timezone.is_naive(dt):
                raise AppError(f"{key} must be an ISO timestamp with a timezone offset.")
            cleaned[key] = dt
    return cleaned


def valid_schedule(event, now):
    if not now < event.registration_closes_at < event.start_at < event.end_at:
        raise conflict("Use future times in this order: registration closes, event starts, event ends.")


@transaction.atomic
def create_event(actor, data):
    require_role(actor, ("Organizer",))
    event = Event(created_by=actor, **validate_fields(data))
    valid_schedule(event, timezone.now())
    event.full_clean()
    event.save()
    return event


@transaction.atomic
def edit_event(actor, event_id, data):
    require_role(actor, ("Organizer",))
    cleaned = validate_fields(data, partial=True)
    event = lock_event(event_id)
    now = timezone.now()
    if event.status == Event.Status.CANCELLED or now >= event.start_at:
        raise conflict("Cancelled or started events cannot be edited.")
    if event.status == Event.Status.PUBLISHED and any(k not in TEXT_FIELDS for k in cleaned):
        raise conflict("After publication, capacity and all event times are fixed.")
    for key, value in cleaned.items():
        setattr(event, key, value)
    if event.status == Event.Status.DRAFT:
        valid_schedule(event, now)
    event.full_clean()
    event.save()
    return event


@transaction.atomic
def publish_event(actor, event_id):
    require_role(actor, ("Organizer",))
    event = lock_event(event_id)
    if event.status == Event.Status.PUBLISHED:
        return event
    if event.status != Event.Status.DRAFT:
        raise conflict("Only a draft event can be published.")
    valid_schedule(event, timezone.now())
    event.status = Event.Status.PUBLISHED
    event.save(update_fields=["status", "updated_at"])
    return event


@transaction.atomic
def cancel_event(actor, event_id, reason):
    from registrations.models import Registration
    require_role(actor, ("Organizer",))
    if not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 500:
        raise AppError("Enter a cancellation reason of 1 to 500 characters.")
    event = lock_event(event_id)
    if event.status == Event.Status.CANCELLED:
        return event
    now = timezone.now()
    if now >= event.start_at:
        raise conflict("An event cannot be cancelled after it starts.")
    event.status = Event.Status.CANCELLED
    event.cancelled_at, event.cancelled_by = now, actor
    event.cancellation_reason = reason.strip()
    event.save(update_fields=["status", "cancelled_at", "cancelled_by", "cancellation_reason", "updated_at"])
    event.registrations.exclude(status=Registration.Status.CANCELLED).update(
        status=Registration.Status.CANCELLED, cancelled_at=now, cancellation_source="Event", attended=False,
        attendance_updated_at=None, attendance_updated_by=None)
    return event

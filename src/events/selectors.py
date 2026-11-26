from datetime import date
from django.db.models import Count, Q
from django.http import Http404
from django.utils import timezone
from accounts.permissions import role_for
from common.errors import AppError
from registrations.models import Registration
from .models import Event


def counted_events():
    return Event.objects.annotate(
        confirmed_count=Count("registrations", filter=Q(registrations__status="Confirmed")),
        waitlisted_count=Count("registrations", filter=Q(registrations__status="Waitlisted")),
        cancelled_count=Count("registrations", filter=Q(registrations__status="Cancelled")),
        attendance_count=Count("registrations", filter=Q(registrations__status="Confirmed", registrations__attended=True)),
    )


def event_list(actor, params):
    query = counted_events()
    if role_for(actor) == "Student":
        query = query.filter(status="Published", start_at__gt=timezone.now())
    q, category, day = (params.get(k, "").strip() for k in ["q", "category", "date"])
    if q:
        query = query.filter(Q(title__icontains=q) | Q(venue__icontains=q))
    if category:
        query = query.filter(category=category)
    if day:
        try:
            parsed = date.fromisoformat(day)
        except ValueError:
            raise AppError("Use a valid date in YYYY-MM-DD format.")
        query = query.filter(start_at__date=parsed)
    return query


def accessible_event(actor, event_id):
    event = counted_events().filter(pk=event_id).first()
    if event is None:
        raise Http404
    if role_for(actor) == "Student":
        if event.status == "Draft" or (event.status == "Cancelled" and not event.registrations.filter(student=actor).exists()):
            raise Http404
    return event


def event_data(event):
    if not hasattr(event, "confirmed_count"):
        event = counted_events().get(pk=event.pk)
    now = timezone.now()
    return {
        "id": event.pk, "title": event.title, "description": event.description,
        "category": event.category, "venue": event.venue,
        "start_at": event.start_at, "end_at": event.end_at,
        "registration_closes_at": event.registration_closes_at,
        "capacity": event.capacity, "status": event.status,
        "confirmed_count": event.confirmed_count, "waitlisted_count": event.waitlisted_count,
        "cancelled_count": event.cancelled_count, "attendance_count": event.attendance_count,
        "remaining_seats": max(0, event.capacity - event.confirmed_count),
        "registration_open": event.status == "Published" and now < event.registration_closes_at,
        "can_edit": event.status != "Cancelled" and now < event.start_at,
        "can_cancel": event.status != "Cancelled" and now < event.start_at,
        "cancellation_reason": event.cancellation_reason,
        "fill_percent": round(100 * event.confirmed_count / event.capacity),
    }


def registration_data(reg):
    rank = None
    if reg.status == "Waitlisted":
        rank = reg.event.registrations.filter(status="Waitlisted").filter(
            Q(joined_at__lt=reg.joined_at) | Q(joined_at=reg.joined_at, id__lte=reg.id)).count()
    return {"registration_id": reg.id, "event_id": reg.event_id,
            "status": reg.status, "queue_rank": rank, "attended": reg.attended,
            "joined_at": reg.joined_at, "confirmed_at": reg.confirmed_at,
            "cancelled_at": reg.cancelled_at, "cancellation_source": reg.cancellation_source}


def personal_records(actor):
    return Registration.objects.filter(student=actor).select_related("event").order_by("-joined_at", "-id")

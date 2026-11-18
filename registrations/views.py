from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from accounts.permissions import page_access
from common.api import endpoint, body
from common.errors import AppError
from events.selectors import personal_records, registration_data, event_data, accessible_event
from . import services


def my_data(actor):
    return [{**registration_data(r), "event": event_data(r.event)} for r in personal_records(actor)]


@page_access("Student")
def mine(request):
    records = my_data(request.user)
    counts = {s.lower(): sum(r["status"] == s for r in records) for s in ["Confirmed", "Waitlisted", "Cancelled"]}
    return render(request, "registrations/mine.html", {"registrations": records, "counts": counts, "nav": "mine"})


@endpoint(["POST"], ("Student",))
def register_api(request, event_id):
    body(request)
    reg, created = services.register(request.user, event_id)
    return JsonResponse(registration_data(reg), status=201 if created else 200)


@endpoint(["GET"], ("Student",))
def mine_api(request):
    return {"registrations": my_data(request.user)}


@endpoint(["POST"], ("Student",))
def cancel_api(request, registration_id):
    body(request)
    return registration_data(services.cancel_registration(request.user, registration_id))


def roster_data(event, status=""):
    if status and status not in ("Confirmed", "Waitlisted", "Cancelled"):
        raise AppError("Choose Confirmed, Waitlisted or Cancelled.")
    query = event.registrations.select_related("student", "student__student_profile").order_by("joined_at", "id")
    if status:
        query = query.filter(status=status)
    records = []
    for reg in query:
        records.append({**registration_data(reg), "student_name": reg.student.get_full_name() or reg.student.username,
                        "student_number": reg.student.student_profile.student_number,
                        "can_mark_attendance": event.status != "Cancelled" and timezone.now() >= event.start_at and reg.status == "Confirmed"})
    return records


@page_access("Organizer")
def roster(request, event_id):
    event = accessible_event(request.user, event_id)
    try:
        records, error = roster_data(event, request.GET.get("status", "")), None
    except AppError as exc:
        records, error = [], exc.message
    return render(request, "registrations/roster.html", {"event": event_data(event), "participants": records, "filter_error": error, "nav": "events"})


@endpoint(["GET"], ("Organizer",))
def roster_api(request, event_id):
    event = accessible_event(request.user, event_id)
    return {"event": event_data(event), "participants": roster_data(event, request.GET.get("status", ""))}


@endpoint(["PATCH"], ("Organizer",))
def attendance_api(request, registration_id):
    return registration_data(services.mark_attendance(request.user, registration_id, body(request, ["attended"]).get("attended")))

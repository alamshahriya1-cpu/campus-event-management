from django.http import JsonResponse
from django.shortcuts import render, redirect
from accounts.permissions import page_access, role_for
from common.api import endpoint, body
from common.errors import AppError
from . import services
from .models import Event
from .selectors import event_list, accessible_event, event_data, registration_data


@page_access("Student", "Organizer")
def home(request):
    return redirect("dashboard" if role_for(request.user) == "Organizer" else "catalog")


@page_access("Student", "Organizer")
def catalog(request):
    error = None
    try:
        events = [event_data(e) for e in event_list(request.user, request.GET)]
    except AppError as exc:
        events, error = [], exc.message
    category_query = Event.objects.all()
    if role_for(request.user) == "Student":
        from django.utils import timezone
        category_query = category_query.filter(status="Published", start_at__gt=timezone.now())
    categories = category_query.order_by("category").values_list("category", flat=True).distinct()
    return render(request, "events/catalog.html", {"events": events, "categories": categories, "filter_error": error, "nav": "events"})


@page_access("Student", "Organizer")
def detail(request, event_id):
    event = accessible_event(request.user, event_id)
    reg = event.registrations.filter(student=request.user).first() if role_for(request.user) == "Student" else None
    return render(request, "events/detail.html", {"event": event_data(event), "registration": registration_data(reg) if reg else None, "nav": "events"})


@page_access("Organizer")
def editor(request, event_id=None):
    event = event_data(accessible_event(request.user, event_id)) if event_id else None
    return render(request, "events/editor.html", {"event": event, "nav": "events"})


@endpoint(["GET", "POST"])
def events_api(request):
    if request.method == "POST":
        event = services.create_event(request.user, body(request, services.EDIT_FIELDS))
        return JsonResponse(event_data(event), status=201)
    return {"events": [event_data(e) for e in event_list(request.user, request.GET)]}


@endpoint(["GET", "PATCH"])
def event_api(request, event_id):
    if request.method == "PATCH":
        return event_data(services.edit_event(request.user, event_id, body(request, services.EDIT_FIELDS)))
    event = accessible_event(request.user, event_id)
    result = event_data(event)
    if role_for(request.user) == "Student":
        reg = event.registrations.filter(student=request.user).first()
        result["my_registration"] = registration_data(reg) if reg else None
    return result


@endpoint(["POST"], ("Organizer",))
def publish_api(request, event_id):
    body(request)
    return event_data(services.publish_event(request.user, event_id))


@endpoint(["POST"], ("Organizer",))
def cancel_api(request, event_id):
    return event_data(services.cancel_event(request.user, event_id, body(request, ["reason"]).get("reason")))

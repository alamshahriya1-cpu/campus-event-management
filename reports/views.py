from django.shortcuts import render
from django.utils import timezone
from accounts.permissions import page_access
from common.api import endpoint
from events.selectors import counted_events, event_data


def dashboard_data():
    events = [event_data(e) for e in counted_events()]
    now = timezone.now()
    upcoming = [e for e in events if e["status"] == "Published" and e["start_at"] > now]
    return {"upcoming_events": len(upcoming), "confirmed": sum(e["confirmed_count"] for e in upcoming),
            "waitlisted": sum(e["waitlisted_count"] for e in upcoming),
            "attendance": sum(e["attendance_count"] for e in events), "events": events}


@page_access("Organizer")
def dashboard(request):
    return render(request, "reports/dashboard.html", {"report": dashboard_data(), "nav": "dashboard"})


@endpoint(["GET"], ("Organizer",))
def dashboard_api(request):
    return dashboard_data()

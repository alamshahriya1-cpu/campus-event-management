from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from accounts.forms import CampusAuthenticationForm
from accounts import user_views
from events import views as event
from registrations import views as registration
from reports import views as report

urlpatterns = [
    path("", event.home, name="home"),
    path("accounts/login/", LoginView.as_view(template_name="accounts/login.html", authentication_form=CampusAuthenticationForm, redirect_authenticated_user=True), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("events/", event.catalog, name="catalog"),
    path("events/new/", event.editor, name="event_new"),
    path("events/<int:event_id>/", event.detail, name="event_detail"),
    path("events/<int:event_id>/edit/", event.editor, name="event_edit"),
    path("events/<int:event_id>/participants/", registration.roster, name="roster"),
    path("my-registrations/", registration.mine, name="my_registrations"),
    path("organizer/", report.dashboard, name="dashboard"),
    path("organizer/users/", user_views.user_list, name="user_list"),
    path("organizer/users/<int:user_id>/edit/", user_views.user_edit, name="user_edit"),
    path("organizer/users/<int:user_id>/password/", user_views.user_password, name="user_password"),
    path("api/events/", event.events_api),
    path("api/events/<int:event_id>/", event.event_api),
    path("api/events/<int:event_id>/publish/", event.publish_api),
    path("api/events/<int:event_id>/cancel/", event.cancel_api),
    path("api/events/<int:event_id>/register/", registration.register_api),
    path("api/events/<int:event_id>/participants/", registration.roster_api),
    path("api/my-registrations/", registration.mine_api),
    path("api/registrations/<int:registration_id>/cancel/", registration.cancel_api),
    path("api/registrations/<int:registration_id>/attendance/", registration.attendance_api),
    path("api/reports/dashboard/", report.dashboard_api),
]

"""Organizer-only pages for existing student accounts; no role or account deletion controls."""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db import IntegrityError, OperationalError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_safe

from .permissions import page_access
from .user_forms import StudentDetailsForm, StudentPasswordForm


def managed_students():
    return (get_user_model().objects.filter(
        groups__name="Student", student_profile__isnull=False,
        is_staff=False, is_superuser=False,
    ).exclude(groups__name="Organizer")
        .select_related("student_profile").distinct()
        .order_by("first_name", "last_name", "username", "pk"))


@never_cache
@page_access("Organizer")
@require_safe
def user_list(request):
    students = managed_students()
    total = students.count()
    query = request.GET.get("q", "").strip()
    error = None
    if len(query) > 150:
        error = "Use no more than 150 characters to search."
        students = students.none()
    else:
        for word in query.split():
            students = students.filter(
                Q(first_name__icontains=word) | Q(last_name__icontains=word)
                | Q(username__icontains=word) | Q(email__icontains=word)
                | Q(student_profile__student_number__icontains=word)
            )
    page = Paginator(students, 25).get_page(request.GET.get("page"))
    return render(request, "accounts/user_list.html", {
        "nav": "users", "page_obj": page, "query": query,
        "total_students": total, "search_error": error,
    }, status=400 if error else 200)


def student_form_page(request, user_id, form_class, template, success_message):
    student = get_object_or_404(managed_students(), pk=user_id)
    form = form_class(student, request.POST if request.method == "POST" else None)
    status = 200
    if request.method == "POST":
        saved = False
        try:
            with transaction.atomic():
                # Refetch under the write transaction before validation and saving.
                student = get_object_or_404(managed_students().select_for_update(), pk=user_id)
                form = form_class(student, request.POST)
                if form.is_valid():
                    form.save()
                    saved = True
        except IntegrityError:
            form.add_error(None, "This change conflicts with another saved account. Check the student ID and try again.")
        except OperationalError as exc:
            if "locked" not in str(exc).lower() and "busy" not in str(exc).lower():
                raise
            form.add_error(None, "The database is busy. Please try again in a moment.")
            status = 503
        if saved:
            messages.success(request, success_message)
            return redirect("user_edit", user_id=student.pk)
        if status == 200:
            status = 400
    response = render(request, template, {"nav": "users", "student": student, "form": form}, status=status)
    if status == 503:
        response["Retry-After"] = "1"
    return response


@never_cache
@page_access("Organizer")
@require_http_methods(["GET", "POST"])
def user_edit(request, user_id):
    return student_form_page(request, user_id, StudentDetailsForm, "accounts/user_edit.html",
                             "Student details saved.")


@sensitive_post_parameters("new_password1", "new_password2")
@never_cache
@page_access("Organizer")
@require_http_methods(["GET", "POST"])
def user_password(request, user_id):
    return student_form_page(request, user_id, StudentPasswordForm, "accounts/user_password.html",
                             "Password reset. The student must sign in again using the new password.")

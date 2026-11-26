"""Organizer-only student provisioning and maintenance; fixed Student permissions."""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db import IntegrityError, OperationalError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_safe

from .permissions import page_access
from .user_forms import (
    StudentAccessForm, StudentCreateForm, StudentDeleteForm,
    StudentDetailsForm, StudentPasswordForm,
)
from .user_lifecycle import deletion_blockers, expire_student_sessions


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


@sensitive_post_parameters("password1", "password2")
@never_cache
@page_access("Organizer")
@require_http_methods(["GET", "POST"])
def user_create(request):
    form = StudentCreateForm(request.POST if request.method == "POST" else None)
    status = 200
    if request.method == "POST":
        student = None
        try:
            with transaction.atomic():
                if form.is_valid():
                    student = form.save()
        except IntegrityError:
            form.add_error(None, "This student ID conflicts with another saved account. Check the ID and try again.")
        except OperationalError as exc:
            if "locked" not in str(exc).lower() and "busy" not in str(exc).lower():
                raise
            form.add_error(None, "The database is busy. Please try again in a moment.")
            status = 503
        else:
            if student is not None:
                messages.success(request, f"Student account created. Sign-in ID: {student.username}.")
                return redirect("user_edit", user_id=student.pk)
        if status == 200:
            status = 400
    response = render(request, "accounts/user_create.html", {"nav": "users", "form": form}, status=status)
    if status == 503:
        response["Retry-After"] = "1"
    return response


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
            student.refresh_from_db()
        except OperationalError as exc:
            if "locked" not in str(exc).lower() and "busy" not in str(exc).lower():
                raise
            form.add_error(None, "The database is busy. Please try again in a moment.")
            status = 503
            student.refresh_from_db()
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
                             "Student details saved. The student signs in with the Student ID shown below.")


@sensitive_post_parameters("new_password1", "new_password2")
@never_cache
@page_access("Organizer")
@require_http_methods(["GET", "POST"])
def user_password(request, user_id):
    return student_form_page(request, user_id, StudentPasswordForm, "accounts/user_password.html",
                             "Password reset. The student must sign in again using the new password.")


def student_action_page(request, user_id, action):
    initial_student = get_object_or_404(managed_students(), pk=user_id)
    student = initial_student
    deleting = action == "delete"

    def make_form(target, data=None):
        return StudentDeleteForm(target, data) if deleting else StudentAccessForm(data)

    form = make_form(student, request.POST if request.method == "POST" else None)
    blockers = deletion_blockers(student) if deleting else []
    status = 200
    if request.method == "POST":
        saved = False
        try:
            with transaction.atomic():
                # SQLite IMMEDIATE serializes writers. Refetch the target and
                # recheck record links after entering the write transaction.
                student = get_object_or_404(managed_students().select_for_update(), pk=user_id)
                form = make_form(student, request.POST)
                blockers = deletion_blockers(student) if deleting else []
                if not form.is_valid():
                    status = 400
                elif blockers:
                    status = 409
                else:
                    if deleting:
                        expire_student_sessions(student)
                        # The profile intentionally PROTECTs its user. Explicit
                        # removal is safe only after the unused-account check;
                        # both deletes roll back if any other protected link exists.
                        student.student_profile.delete()
                        student.delete()
                    else:
                        active = action == "reactivate"
                        if student.is_active != active:
                            student.is_active = active
                            student.save(update_fields=["is_active"])
                            expire_student_sessions(student)
                    saved = True
        except ProtectedError:
            blockers = ["Saved records still reference this account. Keep the account or deactivate it."]
            status = 409
        except IntegrityError:
            form.add_error(None, "This account changed or has linked records. Reload the page and try again.")
            status = 409
        except OperationalError as exc:
            if "locked" not in str(exc).lower() and "busy" not in str(exc).lower():
                raise
            form.add_error(None, "The database is busy. Please try again in a moment.")
            status = 503
        if saved:
            if deleting:
                messages.success(request, f"Unused student account {initial_student.student_profile.student_number} deleted.")
                return redirect("user_list")
            message = (
                "Student account reactivated. The student can sign in again with their existing password."
                if action == "reactivate" else
                "Student account deactivated. Sign-in is blocked; registrations and attendance are preserved."
            )
            messages.success(request, message)
            return redirect("user_edit", user_id=user_id)
        # A failed write may have changed the Python object even after rollback.
        student = initial_student
    response = render(request, "accounts/user_action.html", {
        "nav": "users", "student": student, "form": form,
        "action": action, "blockers": blockers,
    }, status=status)
    if status == 503:
        response["Retry-After"] = "1"
    return response


@never_cache
@page_access("Organizer")
@require_http_methods(["GET", "POST"])
def user_deactivate(request, user_id):
    return student_action_page(request, user_id, "deactivate")


@never_cache
@page_access("Organizer")
@require_http_methods(["GET", "POST"])
def user_reactivate(request, user_id):
    return student_action_page(request, user_id, "reactivate")


@never_cache
@page_access("Organizer")
@require_http_methods(["GET", "POST"])
def user_delete(request, user_id):
    return student_action_page(request, user_id, "delete")

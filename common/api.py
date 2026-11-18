import json
from functools import wraps
from django.core.exceptions import ValidationError
from django.db import OperationalError, IntegrityError
from django.http import JsonResponse, Http404
from django.shortcuts import render
from accounts.permissions import require_role
from .errors import AppError


def endpoint(methods, roles=("Student", "Organizer")):
    def decorator(fn):
        @wraps(fn)
        def wrapped(request, *args, **kwargs):
            try:
                if request.method not in methods:
                    response = JsonResponse({"error": "This method is not allowed.", "code": "method_not_allowed"}, status=405)
                    response["Allow"] = ", ".join(methods)
                    return response
                require_role(request.user, roles)
                result = fn(request, *args, **kwargs)
                response = result if isinstance(result, JsonResponse) else JsonResponse(result)
                response["Cache-Control"] = "no-store"
                return response
            except AppError as exc:
                return JsonResponse({"error": exc.message, "code": exc.code}, status=exc.status)
            except Http404:
                return JsonResponse({"error": "Record not found.", "code": "not_found"}, status=404)
            except ValidationError as exc:
                return JsonResponse({"error": "; ".join(exc.messages), "code": "validation_error"}, status=400)
            except OperationalError as exc:
                if "locked" not in str(exc).lower() and "busy" not in str(exc).lower():
                    raise
                response = JsonResponse({"error": "The database is busy. Please retry in a moment.", "code": "database_busy"}, status=503)
                response["Retry-After"] = "1"
                return response
            except IntegrityError:
                return JsonResponse({"error": "This change conflicts with saved data. Refresh and try again.", "code": "data_conflict"}, status=409)
        return wrapped
    return decorator


def body(request, allowed=()):
    if request.body and request.content_type != "application/json":
        raise AppError("Send a JSON object with Content-Type application/json.")
    try:
        data = json.loads(request.body or b"{}")
    except (ValueError, UnicodeError):
        raise AppError("The request contains invalid JSON.")
    if not isinstance(data, dict):
        raise AppError("The JSON body must be an object.")
    if set(data) - set(allowed):
        raise AppError("The request contains fields that cannot be changed.")
    return data


def csrf_failure(request, reason=""):
    if request.path.startswith("/api/"):
        return JsonResponse({"error": "Your security token has expired or is missing. Refresh the page and try again.", "code": "csrf_failed"}, status=403)
    return render(request, "error.html", {"title": "Please refresh the page", "message": "Your security token has expired or is missing. Reload the page before trying again."}, status=403)

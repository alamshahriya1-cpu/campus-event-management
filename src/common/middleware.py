from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class ApiAuthenticationMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith("/api/") and (not request.user.is_authenticated or not request.user.is_active):
            return JsonResponse({"error": "Please sign in to continue.", "code": "authentication_required"}, status=401)

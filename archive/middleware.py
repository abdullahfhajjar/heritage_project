# archive/middleware.py
from django.utils import translation

class ForceEnglishAdminMiddleware:
    """
    Forces Django Admin to render in English regardless of the user's chosen site language.
    Apply *after* LocaleMiddleware so it can override per-request language.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Adjust the prefix if you mount admin somewhere else
        if request.path.startswith("/admin/"):
            with translation.override("en"):
                return self.get_response(request)
        return self.get_response(request)
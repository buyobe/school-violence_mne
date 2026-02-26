from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.conf import settings

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page
    except those explicitly marked as public.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Public paths that do not require login
        public_paths = [
            settings.LOGIN_URL,              # login page
            '/accounts/logout/',             # logout endpoint
            '/accounts/password_reset/',     # password reset start
            '/accounts/reset/',              # password reset confirm
            '/admin/',                       # admin site
            settings.STATIC_URL,             # static files
            settings.MEDIA_URL if hasattr(settings, "MEDIA_URL") else "/media/",
        ]

        if not request.user.is_authenticated:
            if not any(request.path.startswith(path) for path in public_paths):
                return redirect(settings.LOGIN_URL)

        return self.get_response(request)

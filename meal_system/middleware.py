import logging

from django.conf import settings
from django.http import HttpResponse, JsonResponse


logger = logging.getLogger(__name__)


class CorsMiddleware:
    allow_headers = 'Content-Type, Authorization, X-Requested-With'
    allow_methods = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse(status=204)
            return self._apply_headers(response, request)

        try:
            response = self.get_response(request)
        except Exception:
            logger.exception('Unhandled API exception for %s %s', request.method, request.path)
            response = JsonResponse({'detail': 'Internal server error'}, status=500)
        return self._apply_headers(response, request)

    def _apply_headers(self, response, request):
        origin = request.headers.get('Origin', '').rstrip('/')
        if origin in getattr(settings, 'CORS_ALLOWED_ORIGINS', set()):
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Vary'] = 'Origin'
        response['Access-Control-Allow-Headers'] = self.allow_headers
        response['Access-Control-Allow-Methods'] = self.allow_methods
        response['Access-Control-Max-Age'] = '86400'
        return response

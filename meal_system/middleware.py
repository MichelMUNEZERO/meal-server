from django.http import HttpResponse


class CorsMiddleware:
    allow_origin = '*'
    allow_headers = 'Content-Type, Authorization, X-Requested-With'
    allow_methods = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse(status=204)
            return self._apply_headers(response)

        response = self.get_response(request)
        return self._apply_headers(response)

    def _apply_headers(self, response):
        response['Access-Control-Allow-Origin'] = self.allow_origin
        response['Access-Control-Allow-Headers'] = self.allow_headers
        response['Access-Control-Allow-Methods'] = self.allow_methods
        response['Access-Control-Max-Age'] = '86400'
        return response

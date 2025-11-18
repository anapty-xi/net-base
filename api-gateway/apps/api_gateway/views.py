import requests
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View


@method_decorator(csrf_exempt, name='dispatch')
class ProxyView(View):

    def dispatch(self, request, *args, **kwargs):
        service_name = self.get_service_name(request)
        if not service_name:
            return JsonResponse({'error': 'Service not found'}, status=404)


        service_url = settings.MICROSERVICES.get(service_name)
        if not service_url:
            return JsonResponse({'error': f'Service {service_name} not configured'}, status=500)

        target_url = f"{service_url}{request.path}"

        return self.proxy_request(request, target_url)

    def get_service_name(self, request):
        path = request.path

        if path.startswith('/user/'):
            return 'user-service'
        elif path.startswith('/db/'):
            return 'db-operations-service'
        return None



    def proxy_request(self, request, target_url):
        try:

            headers = {}
            important_headers = [
                'Authorization', 'Content-Type', 'Accept', 'User-Agent',
                'Accept-Language', 'Accept-Encoding'
            ]

            for header_name in important_headers:
                header_value = request.headers.get(header_name)
                if header_value:
                    headers[header_name] = header_value


            data = None
            json_data = None

            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('Content-Type', '')

                if 'application/json' in content_type:
                    try:
                        if request.body:
                            json_data = json.loads(request.body.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        data = request.body
                else:
                    data = request.body


            params = dict(request.GET.items())


            response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                json=json_data,
                data=data if json_data is None else None,
                params=params,
                timeout=30
            )



            django_response = HttpResponse(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('content-type', 'application/json')
            )


            response_headers_to_copy = ['Content-Type', 'Cache-Control', 'ETag']
            for key in response_headers_to_copy:
                if key in response.headers:
                    django_response[key] = response.headers[key]

            return django_response
        except:
            pass



proxy_view = ProxyView.as_view()

import logging
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class LogRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"[REQUEST]\nPath: {request.path},\nMethod: {request.method},\nHeaders:")
        for key, value in request.headers.items():
            print(f"\t{key}: {value}")
        response = self.get_response(request)
        return response


def custom_exception_handler(exc, context):
    # Получаем стандартный ответ от DRF
    response = exception_handler(exc, context)

    # Добавляем дополнительное логирование, если это ошибка
    if response is not None and response.status_code == 400:
        request = context.get('request')
        if request:
            logger.error(
                f"Bad Request: {request.path}\n"
                f"Method: {request.method}\n"
                # f"Body: {request.body.decode('utf-8')}\n"
                f"Errors: {response.data}"
            )

    return response
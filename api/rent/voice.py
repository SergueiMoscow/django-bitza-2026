import json
import os
from datetime import date

import requests
from openai import OpenAI
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from rent.models import Room

# DeepSeek — OpenAI-совместимый API (дешевле Claude, по просьбе пробуем сначала его).
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

RECORD_PAYMENT_TOOL = {
    "type": "function",
    "function": {
        "name": "record_payment",
        "description": (
            "Извлекает данные платежа за аренду помещения, чтобы показать их пользователю "
            "на подтверждение. Вызывай, только если уверенно понятны и номер помещения "
            "(совпадающий с одним из известных), и сумма."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "room": {
                    "type": "string",
                    "description": "Номер помещения, например '2.07'. Должен совпадать с одним из известных номеров.",
                },
                "amount": {"type": "number", "description": "Сумма оплаты в рублях."},
                "discount": {
                    "type": "number",
                    "description": "Скидка в рублях, если явно упомянута в команде. Иначе 0.",
                },
                "date": {"type": "string", "description": "Дата платежа в формате YYYY-MM-DD."},
                "bank_account": {
                    "type": "string",
                    "description": "Счёт/способ получения денег, если упомянут (например Cash, Сбер, Тинькофф).",
                },
            },
            "required": ["room", "amount", "date"],
        },
    },
}


class VoiceTranscribeView(APIView):
    """
    Принимает записанный в браузере аудиофайл, пересылает на собственный self-hosted
    Whisper (onerahmet/openai-whisper-asr-webservice) и возвращает распознанный текст.
    Credentials остаются на бэкенде — фронт про Whisper вообще не знает.
    """
    parser_classes = [MultiPartParser]

    def post(self, request):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({'error': 'Файл не передан'}, status=400)

        url = f"https://{os.environ['WHISPER_URL']}/asr"
        try:
            resp = requests.post(
                url,
                params={'output': 'txt', 'language': 'ru', 'task': 'transcribe', 'encode': 'true'},
                files={'audio_file': (audio_file.name, audio_file.read(), audio_file.content_type)},
                auth=(os.environ['WHISPER_USER'], os.environ['WHISPER_PASS']),
                timeout=60,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            return Response({'error': f'Ошибка распознавания речи: {e}'}, status=502)

        return Response({'text': resp.text.strip()})


class VoiceCommandView(APIView):
    """
    Принимает распознанный речью текст, извлекает через DeepSeek намерение — пока только
    "внести оплату". Сюда не пишется ничего в БД: результат отдаётся пользователю на
    подтверждение, сохранение идёт отдельным запросом на уже существующий payments-эндпоинт.
    """

    def post(self, request):
        text = (request.data.get('text') or '').strip()
        if not text:
            return Response({'error': 'Пустая команда'}, status=400)

        active_rooms = list(
            Room.objects.filter(status='A').order_by('shortname').values_list('shortname', flat=True)
        )
        today = date.today().isoformat()

        system = (
            f"Ты помогаешь вносить оплаты аренды по голосовой команде на русском языке. "
            f"Сегодняшняя дата: {today}. "
            f"Известные номера помещений: {', '.join(active_rooms)}. "
            f"Если из команды однозначно понятны номер помещения (совпадающий с одним из "
            f"известных) и сумма — вызови инструмент record_payment. Дату, если не названа "
            f"явно, ставь сегодняшнюю. Если что-то важное неясно, или названный номер "
            f"помещения не совпадает ни с одним известным — не вызывай инструмент, а задай "
            f"короткий уточняющий вопрос обычным текстом на русском."
        )

        try:
            client = OpenAI(api_key=os.environ['DEEPSEEK_API_KEY'], base_url=DEEPSEEK_BASE_URL)
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                max_tokens=1024,
                tools=[RECORD_PAYMENT_TOOL],
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": text},
                ],
            )
        except Exception as e:
            # Сюда попадает и ошибка API, и отсутствие/некорректность DEEPSEEK_API_KEY —
            # в обоих случаях это ошибка для пользователя, а не повод падать с 500.
            return Response({'error': f'Ошибка распознавания: {e}'}, status=502)

        message = response.choices[0].message
        if message.tool_calls:
            call = message.tool_calls[0]
            intent = json.loads(call.function.arguments)
            return Response({'status': 'confirm', 'intent': intent})

        return Response({
            'status': 'clarify',
            'message': message.content or 'Не удалось распознать команду.',
        })

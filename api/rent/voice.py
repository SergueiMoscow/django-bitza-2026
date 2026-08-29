import json
import os
import re
from datetime import date

import requests
from openai import OpenAI
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from rent.models import Room
from rent.repository import get_user_bank_accounts

# В БД у пользователей не заполнено first_name — эти подписи только для текста промпта.
USER_DISPLAY_NAMES = {'sergey': 'Сергей', 'olga': 'Ольга', 'svetlana': 'Светлана'}

CASH_SYNONYMS = {'нал', 'наличные', 'наличными', 'наличка', 'кэш', 'кеш', 'cash'}

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
                    "description": (
                        "Счёт/способ получения денег, если упомянут — строго одно из значений "
                        "из списка доступных текущему пользователю счетов. Если способ оплаты "
                        "в команде не назван — не указывай это поле вообще."
                    ),
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


def normalize_room_guess(guess: str, known_rooms: list[str]) -> str | None:
    """
    Подстраховка на случай, если модель всё же вернула номер не в том формате
    (например "2.0.1" или "2.1" вместо "2.01" — из-за пауз между цифрами в речи).
    Собирает все цифры, первую считает зданием, остальные — комнатой (дополняя нулём
    слева до двух цифр), и проверяет результат по списку известных номеров.
    """
    if guess in known_rooms:
        return guess
    digits = re.sub(r'\D', '', guess)
    if len(digits) < 2:
        return None
    building, room_digits = digits[0], digits[1:].zfill(2)
    candidate = f'{building}.{room_digits}'
    return candidate if candidate in known_rooms else None


def normalize_bank_account_guess(guess: str, known_accounts: list[str]) -> str | None:
    """
    Сопоставляет то, что вернула модель, со списком счетов, доступных текущему
    пользователю. Отдельно ловит расхождение регистра и бытовые синонимы наличных
    ("нал", "наличка", "кэш" и т.п.) на случай, если модель не подставила точное имя
    счёта из списка, который ей дали.
    """
    if not guess:
        return None
    if guess in known_accounts:
        return guess
    lowered = guess.strip().lower()
    if lowered in CASH_SYNONYMS:
        for candidate in ('Cash', 'Нал'):
            if candidate in known_accounts:
                return candidate
    for name in known_accounts:
        if name.lower() == lowered:
            return name
    return None


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
        account_names = [a['name'] for a in get_user_bank_accounts(request.user)]
        my_name = USER_DISPLAY_NAMES.get(request.user.username, request.user.username)
        today = date.today().isoformat()

        accounts_hint = ''
        if account_names:
            accounts_hint = (
                f"\n\nСчета, на которые может принимать оплату текущий пользователь ({my_name}): "
                f"{', '.join(account_names)}. Поле bank_account заполняй строго одним значением "
                f"из этого списка — не придумывай другие. Если способ оплаты назван словами вроде "
                f"«наличными», «нал», «кэш», «наличка» — выбери из списка счёт, обозначающий "
                f"наличные (например 'Cash' или 'Нал'), если такой есть. Если сказано «мне» или "
                f"названо имя самого пользователя — выбери счёт с его именем, если такой есть в "
                f"списке. Если способ оплаты в команде вообще не упомянут — не указывай "
                f"bank_account, не выбирай наугад."
            )

        system = (
            f"Ты помогаешь вносить оплаты аренды по голосовой команде на русском языке. "
            f"Сегодняшняя дата: {today}. "
            f"Известные номера помещений: {', '.join(active_rooms)}. "
            f"\n\n"
            f"Номера помещений имеют формат '<здание>.<комната>', где часть после точки — "
            f"ВСЕГДА двузначное число ('01', '07', '10' и т.д.), даже если найдено меньше двух "
            f"значащих цифр. В речи цифры комнаты часто называют по одной, иногда с паузами "
            f"между ними — это не значит, что после точки несколько чисел. Например: "
            f"«два ноль один» = 2.01; «два, пауза, один» = 2.01 (не 2.1 и не 2.0.1); "
            f"«один ноль семь» = 1.07; «три ноль пять» = 3.05. Всегда собирай цифры комнаты "
            f"в одно двузначное число (дополняя нулём слева, если названа только одна цифра) "
            f"и сверяй итоговый номер со списком известных — если он не совпал ни с одним "
            f"известным, попробуй другие разумные прочтения тех же цифр, прежде чем сдаваться. "
            f"\n\n"
            f"Если из команды однозначно понятны номер помещения (совпадающий с одним из "
            f"известных) и сумма — вызови инструмент record_payment. Дату, если не названа "
            f"явно, ставь сегодняшнюю. Если что-то важное неясно, или номер помещения "
            f"по-настоящему не удаётся сопоставить ни с одним известным — не вызывай "
            f"инструмент, а задай короткий уточняющий вопрос обычным текстом на русском."
            f"{accounts_hint}"
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
            room = intent.get('room', '')
            if room not in active_rooms:
                normalized = normalize_room_guess(room, active_rooms)
                if normalized:
                    intent['room'] = normalized
                else:
                    return Response({
                        'status': 'clarify',
                        'message': f'Не нашёл помещение «{room}» среди известных — уточните номер.',
                    })
            bank_account = intent.get('bank_account')
            if bank_account:
                intent['bank_account'] = normalize_bank_account_guess(bank_account, account_names)
            return Response({'status': 'confirm', 'intent': intent, 'bank_accounts': account_names})

        return Response({
            'status': 'clarify',
            'message': message.content or 'Не удалось распознать команду.',
        })

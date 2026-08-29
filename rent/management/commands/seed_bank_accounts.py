from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from rent.models import BankAccount

# Реальные названия счетов, встречавшиеся в оплатах ("Тмнькофф" — опечатка "Тинькофф",
# отдельной записи под неё нет).
ACCOUNT_NAMES = [
    'Av.MC', 'Av.RU', 'Cash', 'Tinkoff', 'Авангард', 'Валя', 'Нал', 'Ольга', 'Сбер',
    'Сергей', 'Тинькофф',
]

# Кто на какие счета может принимать оплату (по словам пользователя).
USER_ACCOUNTS = {
    'sergey': ACCOUNT_NAMES,
    'olga': ['Ольга', 'Cash'],
}


class Command(BaseCommand):
    help = 'Заполняет BankAccount и привязку счетов к пользователям (идемпотентно).'

    def handle(self, *args, **options):
        accounts = {}
        for name in ACCOUNT_NAMES:
            account, created = BankAccount.objects.get_or_create(name=name)
            accounts[name] = account
            if created:
                self.stdout.write(f'Создан счёт: {name}')

        for username, account_names in USER_ACCOUNTS.items():
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Пользователь {username} не найден — пропущен'))
                continue
            for name in account_names:
                accounts[name].users.add(user)
            self.stdout.write(f'{username}: {", ".join(account_names)}')

        self.stdout.write(self.style.SUCCESS('Готово.'))

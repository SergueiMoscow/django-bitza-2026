from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from rent.models import Contract, ContractPrint
from rent.repository import get_active_contracts_with_latest_print


class GetActiveContractsWithLatestPrintTest(TestCase):
    def setUp(self):
        # Создаем даты для тестов
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.two_days_ago = self.today - timedelta(days=2)
        self.three_days_ago = self.today - timedelta(days=3)

        # Создаем активные контракты
        self.contract1 = Contract.objects.create(
            name="Contract 1",
            status='A',
            date=self.three_days_ago
        )
        self.contract2 = Contract.objects.create(
            name="Contract 2",
            status='A',
            date=self.two_days_ago
        )
        self.contract3 = Contract.objects.create(
            name="Contract 3",
            status='A',
            date=self.yesterday
        )

        # Создаем неактивный контракт
        self.contract_inactive = Contract.objects.create(
            name="Contract Inactive",
            status='I',
            date=self.today
        )

        # Создаем печати для контрактов
        # Contract1 имеет две печати
        ContractPrint.objects.create(
            contract=self.contract1,
            date=self.yesterday,
            form="Form A1"
        )
        ContractPrint.objects.create(
            contract=self.contract1,
            date=self.two_days_ago,
            form="Form A2"
        )

        # Contract2 имеет одну печать
        ContractPrint.objects.create(
            contract=self.contract2,
            date=self.today,
            form="Form B1"
        )

        # Contract3 не имеет печатей

    def test_get_active_contracts_with_latest_print(self):
        # Вызов функции
        contracts = get_active_contracts_with_latest_print()

        # Проверка количества возвращенных контрактов (должны быть только активные: contract1, contract2, contract3)
        self.assertEqual(contracts.count(), 3, "Должны быть возвращены только активные контракты")

        # Преобразуем queryset в список для удобства
        contracts = list(contracts)

        # Проверка сортировки по sort_date
        # По функции get_queryset в PrintContractsView сортировка по sort_date (увеличению)
        # sort_date = latest_prints[0].date если печати есть, иначе contract.date
        # Соответственно, ожидаемая сортировка:
        # contract3 (нет печатей, date yesterday),
        # contract2 (latest_print date today),
        # contract1 (latest_print date yesterday)
        # Однако, в вашем коде порядок сортировки 'sort_date' по возрастанию, поэтому:
        # contract2 (latest_print date today)
        # contract3 (sort_date yesterday)
        # contract1 (sort_date yesterday)
        # Возможно, стоит проверить это
        # Я предлагаю поменять порядок сортировки на '-sort_date', если требуется от новых к старым

        # Для примера, предположим, что мы следуем текущей реализации и ожидаем сортировку по возрастанию:
        expected_order = [
            self.contract3,  # sort_date = contract.date (yesterday)
            self.contract1,  # sort_date = latest_print date (yesterday)
            self.contract2,  # sort_date = latest_print date (today)
        ]

        self.assertEqual(contracts, expected_order, "Контракты отсортированы неправильно")

    def test_latest_prints_assignment(self):
        # Вызов функции
        contracts = get_active_contracts_with_latest_print()

        for contract in contracts:
            if contract == self.contract1:
                self.assertEqual(len(contract.latest_prints), 2, "Contract1 должен иметь 2 последних печати")
                self.assertEqual(contract.latest_prints[0].date, self.yesterday, "Самая последняя печать Contract1 должна быть вчера")
                self.assertEqual(contract.latest_prints[1].date, self.two_days_ago, "Вторая печать Contract1 должна быть два дня назад")
            elif contract == self.contract2:
                self.assertEqual(len(contract.latest_prints), 1, "Contract2 должен иметь 1 последнюю печать")
                self.assertEqual(contract.latest_prints[0].date, self.today, "Самая последняя печать Contract2 должна быть сегодня")
            elif contract == self.contract3:
                self.assertEqual(len(contract.latest_prints), 0, "Contract3 не должен иметь печатей")

    def test_inactive_contracts_not_returned(self):
        # Вызов функции
        contracts = get_active_contracts_with_latest_print()

        # Проверяем, что неактивный контракт не включен
        self.assertNotIn(self.contract_inactive, contracts, "Неактивный контракт не должен быть возвращен")
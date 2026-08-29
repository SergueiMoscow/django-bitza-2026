from django.db import models
from django.utils import timezone


class GasRecord(models.Model):
    """
    Учёт газовых баллонов — структура 1:1 портирована из bitza_gas_bot/src/models.py
    (SQLAlchemy-модель GasRecord), без изменений полей.
    """
    message_id = models.IntegerField(unique=True)
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    # Дата взятия газа
    gas_taken_date = models.DateTimeField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    capacity = models.IntegerField(default=27, null=True, blank=True)
    room = models.CharField(max_length=20, null=True, blank=True)
    # Дата оплаты
    payment_date = models.DateTimeField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    receiver = models.CharField(max_length=100, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    linked_record = models.ForeignKey(
        'self',
        db_column='linked_record_id',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    # Поля для пользователя
    sender_user_id = models.IntegerField(null=True, blank=True)
    sender_name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'{self.room} — {self.quantity} ({self.date})'

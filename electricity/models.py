from django.contrib.auth.models import User
from django.db import models

from rent.models import Room


class MeterReading(models.Model):
    date = models.DateField(
        verbose_name='Дата'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='readings',
        verbose_name='Комната'
    )
    kwt_count = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        help_text='КВт',
        verbose_name='КВт',
        blank=False,
        null=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        default=0
    )
    created_at = models.DateField(
        verbose_name='Создан',
        auto_now_add=True,
        blank=True,
        null=True
    )
    updated_at = models.DateField(
        verbose_name='Обновлён',
        auto_now=True,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.room} - {self.date} - {self.kwt_count}"

    class Meta:
        unique_together = ('room', 'date')

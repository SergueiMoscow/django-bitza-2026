from django.db import models
from django.contrib.auth.models import User


class Work(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        default=0
    )
    time_begin = models.DateTimeField(
        blank=False,
        verbose_name='Время начала')
    time_end = models.DateTimeField(
        auto_now=False,
        blank=True,
        null=True,
        default=None,
        verbose_name='Время окончания')
    project = models.CharField(max_length=50, verbose_name='Проект', null=True, default=None)
    description = models.TextField(verbose_name='Описание')
    worked_out = models.IntegerField(verbose_name='Отработано времени', null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления')

    class Meta:
        ordering = ['-created_at']


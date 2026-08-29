from django.contrib import admin

from gas.models import GasRecord


@admin.register(GasRecord)
class GasRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'quantity', 'date', 'payment_date', 'amount', 'receiver')
    list_filter = ('room',)
    search_fields = ('room', 'receiver', 'sender_name')
    ordering = ('-date',)

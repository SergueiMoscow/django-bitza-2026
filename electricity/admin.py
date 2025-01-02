# your_app/admin.py

from django.contrib import admin
from .models import MeterReading, Room

@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'kwt_count', 'user', 'created_at', 'updated_at')
    list_filter = ('date', 'room')
    search_fields = ('room__name', 'user__username')
    ordering = ('-date',)
    date_hierarchy = 'date'
    fields = ('room', 'date', 'kwt_count', 'user')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

# @admin.register(Room)
# class RoomAdmin(admin.ModelAdmin):
#     list_display = ('name', 'location')  # Замените на актуальные поля вашей модели
#     search_fields = ('name',)
#     ordering = ('name',)
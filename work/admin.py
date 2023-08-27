from django.contrib import admin
from django.contrib.admin import ModelAdmin

from work.models import Work


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['user', 'time_begin', 'time_end', 'project', 'worked_out']

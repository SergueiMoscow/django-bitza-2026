from django.contrib import admin
from rent.models import Room, Building, ContractForm, Contact, Contract, Payment


class TokensAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'last_login']


admin.site.register(Room, TokensAdmin)

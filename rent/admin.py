from django.contrib import admin
from rent.models import Room, Building, ContractForm, Contact, Contract, Payment, Tokens


# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['shortname', 'building', 'square', 'floor', 'price1', 'description', 'status']
    list_filter = ('building',)
    search_fields = ('shortname',)


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'address1', 'notes']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['surname', 'name', 'birth_date', 'city']
    search_fields = ('surname', 'name', 'city')


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['number', 'room', 'date_begin', 'pay_day', 'price', 'contact', 'status']
    fields = ('number', 'room', 'date_begin', 'date_end', ('price', 'pay_day'), 'discount', 'contact', 'status', 'close_date')
    list_filter = ('status',)
    search_fields = ('room__shortname', 'contact__surname', 'contact__name')
    ordering = ('-date_begin',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['type', 'time', 'date', 'amount', 'discount', 'total', 'bank_account', 'book_account']
    list_filter = ['type', 'time']
    ordering = ('-time',)
    # date_hierarchy = 'time'


@admin.register(Tokens)
class TokensAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'last_used_at']


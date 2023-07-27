from django.contrib import admin
from rent.models import Room, Building, ContractForm, Contact, Contract, Payment, Tokens


# Register your models here.


class RoomAdmin(admin.ModelAdmin):
    list_display = ['shortname', 'building', 'square', 'floor', 'price1', 'description', 'status']
    list_filter = ('building',)
    search_fields = ('shortname',)


class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'address1', 'notes']


class ContactAdmin(admin.ModelAdmin):
    list_display = ['surname', 'name', 'birth_date', 'city']
    search_fields = ('surname', 'name', 'city')


class ContractAdmin(admin.ModelAdmin):
    list_display = ['number', 'room', 'date_begin', 'pay_day', 'price', 'contact', 'status']
    list_filter = ('status',)
    search_fields = ('room__shortname', 'contact__surname', 'contact__name')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['type', 'time', 'date', 'amount', 'discount', 'total', 'bank_account', 'book_account']
    list_filter = ['type', 'time']
    # date_hierarchy = 'time'


class TokensAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'last_used_at']


admin.site.register(Room, RoomAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(ContractForm)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Tokens, TokensAdmin)


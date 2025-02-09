import random
import string

from django.contrib import admin
from django.utils.safestring import mark_safe

from rent.models import Room, Building, ContractForm, Contact, Contract, Payment, Tokens, Document, BankAccount, \
    UserBankAccount
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['shortname', 'building', 'square', 'floor', 'price1', 'description', 'status']
    list_filter = ('building',)
    search_fields = ('shortname',)


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'address1', 'notes']


class DocumentInline(admin.StackedInline):
    model = Document
    extra = 0


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['surname', 'name', 'birth_date', 'city']
    search_fields = ('surname', 'name', 'city')
    inlines = [DocumentInline]


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['number', 'room', 'date_begin', 'pay_day', 'price', 'contact', 'status']
    fields = ('number', 'room', 'date_begin', 'date_end', ('price', 'pay_day'), 'discount', 'contact', 'status', 'close_date')
    list_filter = ('status',)
    search_fields = ('room__shortname', 'contact__surname', 'contact__name')
    ordering = ('-date_begin',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['type', 'room', 'time', 'date', 'amount', 'discount', 'total', 'bank_account', 'book_account']
    list_filter = ['type', 'time']
    ordering = ('-time',)
    # date_hierarchy = 'time'


@admin.register(Tokens)
class TokensAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'last_used_at']

    def save_model(self, request, obj, form, change):
        if len(obj.token) < 30:
            obj.token = ''.join(
                random.choices(string.ascii_letters + string.digits, k=30))
        super().save_model(request, obj, form, change)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['image_file', 'description', 'get_image']

    def get_image(self, obj):
        if obj.image_file:
            return mark_safe(f'<img src="{obj.image_file.url}" width="50">')
        return '-'

    get_image.short_description = 'Изображение'

class UserBankAccountInline(admin.TabularInline):
    model = UserBankAccount
    extra = 1
    # Если есть дополнительные поля в промежуточной модели, они автоматически будут отображены

class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserBankAccountInline]
    # Если есть другие inlines, добавить их в список

# Сначала убрать регистрацию стандартного User
admin.site.unregister(User)
# Затем зарегистрируем его с новым админом
admin.site.register(User, CustomUserAdmin)

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(ContractForm)
class ContractFormAdmin(admin.ModelAdmin):
    ...
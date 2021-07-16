from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['username', 'name', 'phone', 'postal_code', 'email']
    fieldsets = (
        (None, {
            "fields": (
                'username', 'password'
            )
        }),
        (_('Personal Information'), {
            "fields": (
                'name', 'phone', 'postal_code', 'email', 'address', 'title', 'nationality', 'image'
            )
        }),
        (_('Permissions'), {
            "fields": (
                'is_staff', 'is_active', 'is_superuser', 'created_by'
            )
        }),
        (_('Important Dates'), {
            "fields": (
                'last_login', 'birth_date'
            )
        })
    )
    

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Country)
admin.site.register(models.VirtualService)
admin.site.register(models.MarketingGoal)
admin.site.register(models.POSCompany)
admin.site.register(models.PosModel)
admin.site.register(models.POS)
admin.site.register(models.Costumer)
admin.site.register(models.TradingAddress)
admin.site.register(models.Contract)
admin.site.register(models.PaperRoll)
admin.site.register(models.Payment)
admin.site.register(models.MIDRevenue)
admin.site.register(models.ContractPOS)
admin.site.register(models.ContractService)

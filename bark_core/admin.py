from django.contrib import admin
from .models import Account, Transfer

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'balance', 'created_at', 'updated_at')
    search_fields = ('account_number', 'user__username')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('from_account', 'to_account', 'amount', 'timestamp')
    search_fields = ('from_account__account_number', 'to_account__account_number')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# Customize the admin site
admin.site.site_title = "Bark Admin"
admin.site.site_header = "Bark Control Center"

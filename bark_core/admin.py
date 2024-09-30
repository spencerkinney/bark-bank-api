#bark_core/admin.py
from django.contrib import admin
from .models import Account, Transfer

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_masked_account_number', 'balance', 'created_at', 'updated_at')
    search_fields = ('user__username', 'account_number')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def get_masked_account_number(self, obj):
        """Display the last 4 digits of the account number for privacy."""
        return "****" + obj.account_number[-4:]

    get_masked_account_number.short_description = 'Account Number'

    def has_change_permission(self, request, obj=None):
        """Prevent any changes to the account data."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent any account deletions."""
        return False


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('from_account', 'to_account', 'amount', 'timestamp')
    search_fields = ('from_account__account_number', 'to_account__account_number')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)

    def has_change_permission(self, request, obj=None):
        """Prevent changes to transfer records."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of transfer records."""
        return False


# Customize the admin site
admin.site.site_title = "Bark Admin"
admin.site.site_header = "Bark Control Center"

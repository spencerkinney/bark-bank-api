from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from decimal import Decimal
from django.utils import timezone

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='accounts')
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    profile_picture = models.URLField(max_length=1000, blank=True, validators=[URLValidator()])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'account_number']),
        ]

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"

    def clean(self):
        super().clean()
        if self.profile_picture:
            try:
                URLValidator()(self.profile_picture)
            except ValidationError:
                raise ValidationError("Invalid URL for profile picture")

    def deposit(self, amount):
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
        self.balance = self.balance + Decimal(amount)
        self.save(update_fields=['balance', 'updated_at'])

    def withdraw(self, amount):
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive")
        if self.balance < amount:
            raise ValidationError("Insufficient funds")
        self.balance = self.balance - Decimal(amount)
        self.save(update_fields=['balance', 'updated_at'])

class Transfer(models.Model):
    from_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transfers_sent')
    to_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transfers_received')
    amount = models.DecimalField(max_digits=19, decimal_places=4)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['from_account', 'to_account', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.from_account.account_number} -> {self.to_account.account_number}: {self.amount}"

    def clean(self):
        if self.from_account == self.to_account:
            raise ValidationError("Cannot transfer to the same account")
        if self.amount <= 0:
            raise ValidationError("Transfer amount must be positive")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
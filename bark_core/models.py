# bark_core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=16, unique=True)
    balance = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Account {self.account_number[-4:]} - {self.user.username}"

    def deposit(self, amount):
        """Add the given amount to the account's balance."""
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
        self.balance += Decimal(amount)
        self.save(update_fields=['balance', 'updated_at'])

    def withdraw(self, amount):
        """Subtract the given amount from the account's balance."""
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive")
        if self.balance < amount:
            raise ValidationError("Insufficient funds")
        self.balance -= Decimal(amount)
        self.save(update_fields=['balance', 'updated_at'])

    @classmethod
    def verify_account_number(cls, account_number):
        """Verify if an account exists by account number."""
        return cls.objects.filter(account_number=account_number).first()

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
        return f"Transfer from Account {self.from_account.id} to Account {self.to_account.id} of amount {self.amount}"

    def clean(self):
        """Ensure the transfer is valid."""
        if self.from_account == self.to_account:
            raise ValidationError("Cannot transfer to the same account")
        if self.amount <= 0:
            raise ValidationError("Transfer amount must be positive")

    def save(self, *args, **kwargs):
        """Validate the transfer before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

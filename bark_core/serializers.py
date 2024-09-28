from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account, Transfer
from decimal import Decimal

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    initial_deposit = serializers.DecimalField(max_digits=19, decimal_places=4, write_only=True, min_value=Decimal('0.01'))

    class Meta:
        model = Account
        fields = ['id', 'user', 'account_number', 'balance', 'profile_picture', 'created_at', 'initial_deposit']
        read_only_fields = ['balance', 'created_at']

    def create(self, validated_data):
        initial_deposit = validated_data.pop('initial_deposit')
        account = Account.objects.create(**validated_data)
        account.deposit(initial_deposit)
        return account

class TransferSerializer(serializers.ModelSerializer):
    from_account_user = serializers.SerializerMethodField()
    to_account_user = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = ['id', 'from_account', 'to_account', 'amount', 'timestamp', 'from_account_user', 'to_account_user']
        read_only_fields = ['timestamp']

    def get_from_account_user(self, obj):
        return UserSerializer(obj.from_account.user).data

    def get_to_account_user(self, obj):
        return UserSerializer(obj.to_account.user).data

    def validate(self, data):
        if data['from_account'] == data['to_account']:
            raise serializers.ValidationError("Cannot transfer to the same account")
        if data['amount'] <= 0:
            raise serializers.ValidationError("Transfer amount must be positive")
        if data['from_account'].balance < data['amount']:
            raise serializers.ValidationError("Insufficient funds")
        return data

class BalanceSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=19, decimal_places=4, read_only=True)

class TransferHistorySerializer(TransferSerializer):
    pass
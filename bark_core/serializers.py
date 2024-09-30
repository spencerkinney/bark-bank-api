# bark_core/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account, Transfer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AccountSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)  # Accept user_id on POST
    user_detail = UserSerializer(read_only=True, source='user')  # Use UserSerializer for read operations
    initial_deposit = serializers.DecimalField(max_digits=19, decimal_places=2, write_only=True)
    account_number = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = ['id', 'user', 'user_detail', 'account_number', 'balance', 'initial_deposit', 'created_at']
        read_only_fields = ['id', 'balance', 'created_at']

    def validate_account_number(self, value):
        if Account.verify_account_number(value):
            raise serializers.ValidationError("An account with this number already exists.")
        return value

    def create(self, validated_data):
        initial_deposit = validated_data.pop('initial_deposit')
        account_number = validated_data.pop('account_number')
        user = validated_data.pop('user')  # This now accepts the user ID

        account = Account.objects.create(
            user=user,
            account_number=account_number,
            balance=initial_deposit
        )
        return account

class TransferSerializer(serializers.ModelSerializer):
    from_account_number = serializers.CharField(write_only=True)
    to_account_number = serializers.CharField(write_only=True)
    amount = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        model = Transfer
        fields = ['id', 'from_account_number', 'to_account_number', 'amount', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def validate(self, data):
        from_account = Account.verify_account_number(data['from_account_number'])
        to_account = Account.verify_account_number(data['to_account_number'])

        if not from_account or not to_account:
            raise serializers.ValidationError("One or both of the account numbers are invalid.")

        data['from_account'] = from_account
        data['to_account'] = to_account

        if from_account == to_account:
            raise serializers.ValidationError("Cannot transfer to the same account.")

        return data

    def create(self, validated_data):
        from_account = validated_data.pop('from_account')
        to_account = validated_data.pop('to_account')
        amount = validated_data.pop('amount')

        # Ensure enough funds before creating transfer
        if from_account.balance < amount:
            raise serializers.ValidationError("Insufficient funds in the account.")

        transfer = Transfer.objects.create(
            from_account=from_account,
            to_account=to_account,
            amount=amount
        )

        return transfer

class BalanceSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=19, decimal_places=4, read_only=True)

class TransferHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['id', 'from_account', 'to_account', 'amount', 'timestamp']

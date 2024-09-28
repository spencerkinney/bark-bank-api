from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import User, Account, Transfer
from .serializers import UserSerializer, AccountSerializer, TransferSerializer, BalanceSerializer, TransferHistorySerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Security: Ensure all endpoints require authentication

    # Security: Restrict users to only view their own user details
    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id)

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    # Override to remove user filtering; agents can access all accounts
    def get_queryset(self):
        return self.queryset

    def perform_create(self, serializer):
        initial_deposit = serializer.validated_data.get('initial_deposit')
        if initial_deposit is None or initial_deposit <= 0:
            raise ValidationError("Initial deposit must be a positive amount.")
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        account = self.get_object()
        serializer = BalanceSerializer({'balance': account.balance})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def transfers(self, request, pk=None):
        account = self.get_object()
        transfers = Transfer.objects.filter(from_account=account) | Transfer.objects.filter(to_account=account)
        transfers = transfers.order_by('-timestamp')
        serializer = TransferHistorySerializer(transfers, many=True)
        return Response(serializer.data)

class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    @transaction.atomic  # Data Integrity: Ensure atomicity of transfer operations
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from_account = serializer.validated_data['from_account']
        to_account = serializer.validated_data['to_account']
        amount = Decimal(serializer.validated_data['amount'])

        # Validation: Prevent same-account transfers
        if from_account == to_account:
            return Response({"detail": "Cannot transfer to the same account."}, status=status.HTTP_400_BAD_REQUEST)

        # Validation: Ensure positive transfer amount
        if amount <= 0:
            return Response({"detail": "Transfer amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        # Validation: Check for sufficient funds
        if from_account.balance < amount:
            return Response({"detail": "Insufficient funds for transfer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():  # Data Integrity: Ensure both operations succeed or fail together
                from_account.withdraw(amount)
                to_account.deposit(amount)
                transfer = serializer.save()
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # Allow viewing all transfers regardless of the user
    def get_queryset(self):
        return self.queryset.order_by('-timestamp')

# TODO: Implement rate limiting to prevent abuse
# TODO: Add comprehensive logging for all transactions
# TODO: Implement multi-factor authentication for high-value transactions
# TODO: Use HTTPS for all API communications
# TODO: Implement proper API versioning
# TODO: Add detailed reconciliation and reporting features
# TODO: Implement robust error tracking and monitoring
# TODO: Implementing network idempotency for transfer operations

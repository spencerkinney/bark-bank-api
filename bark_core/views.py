# bark_core/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import IntegrityError
import logging

from .models import Account, Transfer
from .serializers import UserSerializer, AccountSerializer, TransferSerializer, BalanceSerializer, TransferHistorySerializer

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.select_related('user').all()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            account = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(self.get_serializer(account).data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({"detail": "An account with this number already exists."}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        if not self.request.user.is_staff and serializer.validated_data['user'] != self.request.user:
            raise PermissionDenied("You don't have permission to create an account for another user.")
        try:
            account = serializer.save()
            logger.info(f"Account created: {account.id}")
            return account
        except Exception as e:
            logger.error(f"Error creating account: {str(e)}")
            raise

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        account = self.get_object()
        serializer = BalanceSerializer({'balance': account.balance})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def transfers(self, request, pk=None):
        account = self.get_object()
        transfers = Transfer.objects.filter(Q(from_account=account) | Q(to_account=account))
        transfers = transfers.order_by('-timestamp')
        serializer = TransferHistorySerializer(transfers, many=True)
        return Response(serializer.data)

    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_staff and obj.user != self.request.user:
            raise PermissionDenied("You don't have permission to access this account.")
        return obj


class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.all()
    serializer_class = TransferSerializer
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from_account = serializer.validated_data['from_account']
        to_account = serializer.validated_data['to_account']
        amount = Decimal(serializer.validated_data['amount'])

        if not self.request.user.is_staff and from_account.user != self.request.user:
            raise PermissionDenied("You don't have permission to transfer from this account.")

        try:
            # Deduct the amount from the source account
            from_account.withdraw(amount)

            # Add the amount to the destination account
            to_account.deposit(amount)

            # Save the transfer record
            transfer = serializer.save()

            logger.info(f"Transfer created: {transfer.id}")
        except ValidationError as e:
            logger.error(f"Transfer validation error: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Transfer error: {str(e)}")
            return Response({"detail": "An error occurred during the transfer."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = self.queryset.select_related('from_account', 'to_account')
        if self.request.user.is_staff:
            return queryset
        user_accounts = Account.objects.filter(user=self.request.user)
        return queryset.filter(Q(from_account__in=user_accounts) | Q(to_account__in=user_accounts))

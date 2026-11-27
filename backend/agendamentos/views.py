from datetime import timedelta

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Agendamento, Quadra
from .serializers import AgendamentoSerializer, QuadraSerializer


class QuadraViewSet(viewsets.ModelViewSet):
    serializer_class = QuadraSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Quadra.objects.all()
        return Quadra.objects.filter(ativa=True)


class AgendamentoViewSet(viewsets.ModelViewSet):
    serializer_class = AgendamentoSerializer
    queryset = Agendamento.objects.select_related("quadra").all()

    def get_permissions(self):
        if self.action in ["create", "pagar", "cancelar", "list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        limite_expiracao = timezone.now() - timedelta(minutes=10)
        Agendamento.objects.filter(
            status=Agendamento.Status.PENDENTE,
            criado_em__lt=limite_expiracao,
        ).update(status=Agendamento.Status.EXPIRADO)

        qs = super().get_queryset()
        data = self.request.query_params.get("data")
        data_inicio = self.request.query_params.get("data_inicio")
        data_fim = self.request.query_params.get("data_fim")

        if data:
            qs = qs.filter(data=data)
        if data_inicio:
            qs = qs.filter(data__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data__lte=data_fim)
        return qs

    @action(detail=True, methods=["post"])
    def pagar(self, request, pk=None):
        agendamento = self.get_object()

        if agendamento.status != Agendamento.Status.PENDENTE:
            return Response(
                {"detail": f"Agendamento não pode ser pago (status atual: {agendamento.status})."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if agendamento.esta_expirado:
            agendamento.status = Agendamento.Status.EXPIRADO
            agendamento.save(update_fields=["status"])
            return Response(
                {"detail": "Tempo de 10 minutos para pagamento expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        agendamento.status = Agendamento.Status.CONFIRMADO
        agendamento.save(update_fields=["status"])
        return Response(self.get_serializer(agendamento).data)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        agendamento = self.get_object()

        if agendamento.status == Agendamento.Status.CANCELADO:
            return Response(
                {"detail": "Agendamento já está cancelado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        agendamento.status = Agendamento.Status.CANCELADO
        agendamento.cancelado_em = timezone.now()
        agendamento.save(update_fields=["status", "cancelado_em"])
        return Response(self.get_serializer(agendamento).data)
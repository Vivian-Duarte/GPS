from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Agendamento, Quadra


class QuadraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quadra
        fields = ["id", "nome", "tipo_piso", "valor_hora", "ativa"]


class AgendamentoSerializer(serializers.ModelSerializer):
    expira_em = serializers.DateTimeField(read_only=True)
    quadra_nome = serializers.CharField(source="quadra.nome", read_only=True)

    class Meta:
        model = Agendamento
        fields = [
            "id",
            "quadra",
            "quadra_nome",
            "nome_cliente",
            "telefone_cliente",
            "data",
            "horario_inicio",
            "status",
            "criado_em",
            "expira_em",
            "cancelado_em",
        ]
        read_only_fields = ["status", "criado_em", "expira_em", "cancelado_em"]

    def validate(self, attrs):
        quadra = attrs["quadra"]
        data = attrs["data"]
        horario_inicio = attrs["horario_inicio"]
        telefone = attrs["telefone_cliente"]

        if not quadra.ativa:
            raise serializers.ValidationError("Esta quadra não está ativa para agendamentos.")

        limite_expiracao = timezone.now() - timedelta(minutes=10)
        Agendamento.objects.filter(
            status=Agendamento.Status.PENDENTE,
            criado_em__lt=limite_expiracao,
        ).update(status=Agendamento.Status.EXPIRADO)

        status_ativos = [Agendamento.Status.PENDENTE, Agendamento.Status.CONFIRMADO]

        conflito = Agendamento.objects.filter(
            quadra=quadra,
            data=data,
            horario_inicio=horario_inicio,
            status__in=status_ativos,
        ).exists()
        if conflito:
            raise serializers.ValidationError("Este horário já está reservado para esta quadra.")

        total_dia_cliente = Agendamento.objects.filter(
            telefone_cliente=telefone,
            data=data,
            status__in=status_ativos,
        ).count()
        if total_dia_cliente >= 2:
            raise serializers.ValidationError(
                "Limite atingido: cada cliente pode agendar no máximo 2 horários por dia."
            )

        return attrs
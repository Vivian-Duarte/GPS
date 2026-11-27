from datetime import timedelta

from django.db import models
from django.utils import timezone


class Quadra(models.Model):
    nome = models.CharField(max_length=100)
    tipo_piso = models.CharField(max_length=50)
    valor_hora = models.DecimalField(max_digits=8, decimal_places=2)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return f"{self.nome} ({self.tipo_piso})"


class Agendamento(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente de Pagamento"
        CONFIRMADO = "CONFIRMADO", "Confirmado"
        CANCELADO = "CANCELADO", "Cancelado"
        EXPIRADO = "EXPIRADO", "Expirado"

    quadra = models.ForeignKey(
        Quadra,
        on_delete=models.PROTECT,
        related_name="agendamentos",
    )
    nome_cliente = models.CharField(max_length=120)
    telefone_cliente = models.CharField(max_length=20, db_index=True)
    data = models.DateField(db_index=True)
    horario_inicio = models.TimeField()
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    cancelado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["data", "horario_inicio"]

    @property
    def expira_em(self):
        return self.criado_em + timedelta(minutes=10)

    @property
    def esta_expirado(self) -> bool:
        return (
            self.status == self.Status.PENDENTE
            and timezone.now() > self.expira_em
        )

    def __str__(self) -> str:
        return f"{self.quadra.nome} - {self.data} {self.horario_inicio} ({self.nome_cliente})"
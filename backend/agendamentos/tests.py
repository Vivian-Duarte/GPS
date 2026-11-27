from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Agendamento, Quadra


class QuadraAPITestCase(APITestCase):
    def setUp(self):
        self.quadra_ativa = Quadra.objects.create(
            nome="Quadra 1",
            tipo_piso="Saibro",
            valor_hora="80.00",
            ativa=True,
        )
        self.quadra_inativa = Quadra.objects.create(
            nome="Quadra 2",
            tipo_piso="Rápida",
            valor_hora="90.00",
            ativa=False,
        )
        self.url_list = reverse("quadra-list")

    def test_listar_apenas_quadras_ativas_publicamente(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nome"], "Quadra 1")

    def test_criar_quadra_exige_autenticacao(self):
        payload = {
            "nome": "Quadra 3",
            "tipo_piso": "Saibro",
            "valor_hora": "100.00",
            "ativa": True,
        }
        # Sem login deve bloquear
        response_anon = self.client.post(self.url_list, payload, format="json")
        self.assertEqual(response_anon.status_code, status.HTTP_401_UNAUTHORIZED)

        # Com login do proprietário deve permitir
        user = User.objects.create_user(username="dono", password="senha123")
        self.client.force_authenticate(user=user)
        response_auth = self.client.post(self.url_list, payload, format="json")
        self.assertEqual(response_auth.status_code, status.HTTP_201_CREATED)


class AgendamentoAPITestCase(APITestCase):
    def setUp(self):
        self.quadra = Quadra.objects.create(
            nome="Quadra Central",
            tipo_piso="Saibro",
            valor_hora="85.00",
            ativa=True,
        )
        self.data_reserva = date.today() + timedelta(days=1)
        self.url_list = reverse("agendamento-list")

    def _payload(self, horario="10:00:00", telefone="31999990000"):
        return {
            "quadra": self.quadra.id,
            "nome_cliente": "João Silva",
            "telefone_cliente": telefone,
            "data": self.data_reserva.isoformat(),
            "horario_inicio": horario,
        }

    def test_criar_agendamento_sucesso(self):
        response = self.client.post(self.url_list, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Agendamento.Status.PENDENTE)

    def test_bloquear_conflito_horario(self):
        self.client.post(self.url_list, self._payload("10:00:00", "31999990001"), format="json")
        response = self.client.post(
            self.url_list,
            self._payload("10:00:00", "31999990002"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_limite_dois_agendamentos_por_dia_por_telefone(self):
        self.client.post(self.url_list, self._payload("08:00:00"), format="json")
        self.client.post(self.url_list, self._payload("09:00:00"), format="json")

        # Terceiro agendamento no mesmo dia com o mesmo telefone deve falhar
        response = self.client.post(self.url_list, self._payload("10:00:00"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pagar_dentro_do_prazo(self):
        agendamento = Agendamento.objects.create(
            quadra=self.quadra,
            nome_cliente="Maria",
            telefone_cliente="31988887777",
            data=self.data_reserva,
            horario_inicio=time(14, 0),
        )
        url_pagar = reverse("agendamento-pagar", args=[agendamento.id])
        response = self.client.post(url_pagar)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Agendamento.Status.CONFIRMADO)

    def test_pagar_apos_10_minutos_expira(self):
        agendamento = Agendamento.objects.create(
            quadra=self.quadra,
            nome_cliente="Carlos",
            telefone_cliente="31977776666",
            data=self.data_reserva,
            horario_inicio=time(15, 0),
        )
        # Simula que o agendamento foi criado há 11 minutos
        Agendamento.objects.filter(pk=agendamento.pk).update(
            criado_em=timezone.now() - timedelta(minutes=11)
        )

        url_pagar = reverse("agendamento-pagar", args=[agendamento.id])
        response = self.client.post(url_pagar)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        agendamento.refresh_from_db()
        self.assertEqual(agendamento.status, Agendamento.Status.EXPIRADO)

    def test_cancelar_agendamento_libera_horario(self):
        agendamento = Agendamento.objects.create(
            quadra=self.quadra,
            nome_cliente="Ana",
            telefone_cliente="31966665555",
            data=self.data_reserva,
            horario_inicio=time(16, 0),
            status=Agendamento.Status.CONFIRMADO,
        )
        url_cancelar = reverse("agendamento-cancelar", args=[agendamento.id])
        response = self.client.post(url_cancelar)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Agendamento.Status.CANCELADO)
        self.assertIsNotNone(response.data["cancelado_em"])

        # Outro cliente deve conseguir reservar o horário liberado
        nova_reserva = self.client.post(
            self.url_list,
            self._payload("16:00:00", "31955554444"),
            format="json",
        )
        self.assertEqual(nova_reserva.status_code, status.HTTP_201_CREATED)
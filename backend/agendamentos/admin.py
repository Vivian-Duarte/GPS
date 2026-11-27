from django.contrib import admin

from .models import Agendamento, Quadra


@admin.register(Quadra)
class QuadraAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo_piso", "valor_hora", "ativa")
    list_filter = ("ativa", "tipo_piso")
    search_fields = ("nome",)
    list_editable = ("ativa",)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = (
        "quadra",
        "data",
        "horario_inicio",
        "nome_cliente",
        "telefone_cliente",
        "status",
        "criado_em",
    )
    list_filter = ("status", "data", "quadra")
    search_fields = ("nome_cliente", "telefone_cliente")
    readonly_fields = ("criado_em", "cancelado_em")
    ordering = ("-data", "horario_inicio")
    
admin.site.site_header = "Gestão de Quadras"
admin.site.site_title = "Gestão de Quadras"
admin.site.index_title = "Painel Administrativo"
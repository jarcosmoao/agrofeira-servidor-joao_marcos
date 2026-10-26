from django.contrib import admin
from .models import Pedido, ItemPedido, PontoRetirada


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "comprador",
        "ponto_retirada",
        "situacao",
        "criado_em",
    )

    list_filter = (
        "situacao",
        "ponto_retirada",
    )

    search_fields = (
        "comprador",
        "telefone",
    )

    inlines = [ItemPedidoInline]


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pedido",
        "produto",
        "quantidade",
        "preco_unitario_centavos",
    )

@admin.register(PontoRetirada)
class PontoRetiradaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "endereco",
        "horario",
    )

    list_filter = (
        "produtores",
    )

    search_fields = (
        "nome",
        "endereco",
    )
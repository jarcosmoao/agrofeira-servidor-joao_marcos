from collections import defaultdict
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.template.defaultfilters import floatformat
from catalogo.models import Produto
from catalogo.templatetags.moeda import reais
from . import carrinho as cesta
from .models import Pedido, ItemPedido


def validar_quantidade(produto, quantidade):
    """Recusa a quantidade que não vale para o produto.

    Quem decide é o servidor: o navegador só ajuda.
    """
    if quantidade <= 0:
        raise ValidationError(
            f"{produto.nome}: a quantidade tem que ser maior que zero."
        )

    inteira = quantidade == quantidade.to_integral_value()

    if not produto.unidade.fracionavel and not inteira:
        raise ValidationError(
            f"{produto.nome}: a unidade ({produto.unidade.nome}) "
            "não aceita quantidade quebrada."
        )

    if quantidade > produto.estoque:
        raise ValidationError(
            f"Estoque de {produto.nome}: "
            f"{floatformat(produto.estoque, '-3')} "
            f"{produto.unidade.sigla}. Você pediu "
            f"{floatformat(quantidade, '-3')}."
        )


def criar_pedido(carrinho, dados):
    if not carrinho:
        raise ValidationError(
            "Seu carrinho está vazio. Adicione produtos antes de finalizar."
        )

    itens = cesta.detalhar(carrinho)

    if len(itens) != len(carrinho):
        raise ValidationError(
            "Um ou mais produtos do carrinho não estão mais disponíveis. "
            "Esvazie o carrinho e monte seu pedido novamente."
        )

    totais_por_produtor = defaultdict(int)

    for item in itens:
        produto = item["produto"]
        quantidade = item["quantidade"]

        validar_quantidade(produto, quantidade)

        totais_por_produtor[produto.produtor] += (
            item["subtotal_centavos"]
        )

    for produtor, total in totais_por_produtor.items():
        minimo = produtor.pedido_minimo_centavos

        if total < minimo:
            falta = minimo - total

            raise ValidationError(
                f"O pedido para {produtor.nome} não atingiu o mínimo. "
                f"Faltam {reais(falta)} para completar o valor mínimo."
            )

    with transaction.atomic():
        pedido = Pedido.objects.create(**dados)

        for item in itens:
            produto = item["produto"]
            quantidade = item["quantidade"]

            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                nome_produto=produto.nome,
                nome_produtor=produto.produtor.nome,
                nome_unidade=produto.unidade.nome,
                preco_unitario_centavos=produto.preco_centavos,
                quantidade=quantidade,
            )

            atualizados = Produto.objects.filter(
                pk=produto.pk,
                estoque__gte=quantidade,
            ).update(
                estoque=F("estoque") - quantidade
            )

            if atualizados == 0:
                raise ValidationError(
                    f"Estoque insuficiente para {produto.nome}. "
                    "Atualize seu carrinho e tente novamente."
                )

    return pedido

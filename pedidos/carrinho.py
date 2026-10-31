from decimal import ROUND_HALF_UP, Decimal

from catalogo.models import Produto

CHAVE = "carrinho"


def ler(sessao):
    """O carrinho como está na sessão."""
    return sessao.get(CHAVE, {})


def adicionar(sessao, produto, quantidade):
    carrinho = sessao.setdefault(CHAVE, {})
    atual = Decimal(carrinho.get(str(produto.pk), "0"))
    carrinho[str(produto.pk)] = str(atual + quantidade)
    sessao.modified = True


def esvaziar(sessao):
    sessao.pop(CHAVE, None)


def subtotal_centavos(preco_centavos, quantidade):
    """Preço vezes quantidade, arredondado para o centavo."""
    valor = preco_centavos * quantidade
    return int(
        valor.quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )


def itens(sessao):
    """Os itens do carrinho da sessão."""
    return detalhar(ler(sessao))


def detalhar(carrinho):
    """Transforma o dicionário em uma lista de itens."""
    ids = [int(pk) for pk in carrinho]

    produtos = Produto.objects.filter(pk__in=ids)
    produtos = produtos.select_related("produtor", "unidade")

    por_id = {p.pk: p for p in produtos}
    resultado = []

    for pk, texto in carrinho.items():
        produto = por_id.get(int(pk))

        if produto is None:
            continue

        quantidade = Decimal(texto)
        subtotal = subtotal_centavos(
            produto.preco_centavos,
            quantidade
        )

        resultado.append({
            "produto": produto,
            "quantidade": quantidade,
            "subtotal_centavos": subtotal,
        })

    return resultado


def total_centavos(itens):
    return sum(item["subtotal_centavos"] for item in itens)
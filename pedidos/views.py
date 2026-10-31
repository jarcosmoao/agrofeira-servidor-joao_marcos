from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST
from . import carrinho
from .forms import FechamentoForm
from .models import Pedido
from .servicos import criar_pedido


def ver_carrinho(request):
    itens = carrinho.itens(request.session)

    contexto = {
        "itens": itens,
        "total_centavos": carrinho.total_centavos(itens),
    }

    return render(request, "pedidos/carrinho.html", contexto)


@require_POST
def esvaziar(request):
    carrinho.esvaziar(request.session)

    messages.success(request, "Carrinho esvaziado.")

    return redirect("pedidos:carrinho")


def checkout(request):
    carrinho_atual = carrinho.ler(request.session)

    if not carrinho_atual:
        messages.error(
            request,
            "Seu carrinho está vazio. Adicione produtos antes de finalizar."
        )
        return redirect("pedidos:carrinho")

    itens = carrinho.detalhar(carrinho_atual)

    contexto = {
        "form": FechamentoForm(),
        "itens": itens,
        "total_centavos": carrinho.total_centavos(itens),
    }

    if request.method == "POST":
        form = FechamentoForm(request.POST)

        if form.is_valid():
            try:
                pedido = criar_pedido(
                    carrinho_atual,
                    form.cleaned_data,
                )
            except ValidationError as erro:
                form.add_error(None, erro)
            else:
                carrinho.esvaziar(request.session)
                messages.success(request, "Pedido recebido!")

                return redirect(
                    "pedidos:pedido",
                    codigo=pedido.codigo,
                )

        contexto["form"] = form

    return render(request, "pedidos/checkout.html", contexto)


def confirmar_pedido(request, codigo):
    pedido = get_object_or_404(
        Pedido,
        codigo=codigo,
    )

    itens = []

    for item in pedido.itens.all():
        subtotal = carrinho.subtotal_centavos(
            item.preco_unitario_centavos,
            item.quantidade,
        )

        itens.append({
            "produto": {
                "nome": item.nome_produto,
                "produtor": item.nome_produtor,
                "unidade": item.nome_unidade,
            },
            "quantidade": item.quantidade,
            "subtotal_centavos": subtotal,
            "preco_unitario_centavos": item.preco_unitario_centavos,
        })

    contexto = {
        "pedido": pedido,
        "itens": itens,
        "total_centavos": carrinho.total_centavos(itens),
    }

    return render(request, "pedidos/pedido.html", contexto)

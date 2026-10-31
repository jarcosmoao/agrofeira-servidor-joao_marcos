from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import carrinho


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
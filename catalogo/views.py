from django.http import Http404
from django.shortcuts import render
from .dados import PRODUTOS, PRODUTORES


def home(request):
    destaques = [p for p in PRODUTOS if p["destaque"]]
    contexto = {"destaques": destaques, "total": len(PRODUTOS)}
    return render(request, "catalogo/home.html", contexto)


def produtos(request):
    return render(
        request,
        "catalogo/produto_lista.html",
        {"produtos": PRODUTOS}
    )


def produto(request, slug):
    for p in PRODUTOS:
        if p["slug"] == slug:
            contexto = {"produto": p}
            p["preco_reais"] = p["preco_centavos"] / 100
            return render(
                request,
                "catalogo/produto_detalhe.html",
                contexto
            )
    raise Http404("Nenhum produto com esse endereço.")


def produtores(request):
    busca = request.GET.get("q", "").strip()

    lista_produtores = PRODUTORES

    if busca:
        termo = busca.casefold()

        lista_produtores = [
            p for p in PRODUTORES
            if termo in p["nome"].casefold()
            or termo in p["comunidade"].casefold()
        ]

    contexto = {
        "produtores": lista_produtores,
        "busca": busca,
    }

    return render(
        request,
        "catalogo/produtor_lista.html",
        contexto
    )


def produtor(request, slug):
    produtor_encontrado = None

    for p in PRODUTORES:
        if p["slug"] == slug:
            produtor_encontrado = p
            break

    if produtor_encontrado is None:
        raise Http404("Nenhum produtor com esse endereço.")

    produtos_do_produtor = [
        p for p in PRODUTOS
        if p["produtor"] == produtor_encontrado
    ]

    contexto = {
        "produtor": produtor_encontrado,
        "produtos": produtos_do_produtor,
    }

    return render(
        request,
        "catalogo/produtor_detalhe.html",
        contexto
    )
from django.shortcuts import get_object_or_404, redirect, render
from .models import Produto, Produtor
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Q


def home(request):
    mes = timezone.localdate().month

    destaques = (
        Produto.objects.disponiveis_em(mes)
        .filter(destaque=True)
        .select_related("categoria", "produtor", "unidade")
    )

    contexto = {
        "destaques": destaques,
        "total": Produto.objects.count(),
    }

    return render(request, "catalogo/home.html", contexto)

def produtos(request):
    busca = request.GET.get("q", "")
    lista = Produto.objects.all()

    if busca:
        lista = lista.filter(nome__icontains=busca)

    contexto = {
        "produtos": lista,
        "busca": busca,
    }
    return render(request, "catalogo/produto_lista.html", contexto)


def produto(request, slug):
    p = get_object_or_404(Produto, slug=slug)
    return render(
        request,
        "catalogo/produto_detalhe.html",
        {"produto": p},
    )


def catalogo_antigo(request):
    return redirect("catalogo:produtos", permanent=True)

def produtores(request):
    busca = request.GET.get("q", "")

    lista = (
        Produtor.objects.annotate(num_produtos=Count("produtos"))
        .prefetch_related("propriedades")
        .order_by("nome")
    )

    if busca:
        lista = lista.filter(
            Q(nome__icontains=busca) | Q(comunidade__icontains=busca)
        )

    pagina = Paginator(lista, 4).get_page(request.GET.get("page"))

    parametros = request.GET.copy()
    parametros.pop("page", None)
    parametros = parametros.urlencode()

    if parametros:
        parametros += "&"

    contexto = {
        "page_obj": pagina,
        "busca": busca,
        "parametros": parametros,
    }

    return render(request, "catalogo/produtor_lista.html", contexto)

def produtor(request, slug):
    pr = get_object_or_404(Produtor, slug=slug)
    contexto = {
        "produtor": pr,
        "produtos": pr.produtos.all(),
    }
    return render(
        request,
        "catalogo/produtor_detalhe.html",
        contexto,
    )
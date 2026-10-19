from django import template

register = template.Library()


@register.filter
def reais(valor_centavos):
    valor = valor_centavos / 100
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
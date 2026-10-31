from django.core.exceptions import ValidationError
from django.template.defaultfilters import floatformat


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
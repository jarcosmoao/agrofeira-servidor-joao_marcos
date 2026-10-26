from django.db import models
from catalogo.models import Produto, Produtor


class PontoRetirada(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    horario = models.CharField(max_length=200)

    produtores = models.ManyToManyField(
        Produtor,
        related_name="pontos_retirada",
        blank=True,
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Ponto de retirada"
        verbose_name_plural = "Pontos de retirada"

    def __str__(self):
        return self.nome

class Pedido(models.Model):
    comprador = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)

    ponto_retirada = models.ForeignKey(
        PontoRetirada,
        on_delete=models.PROTECT,
        related_name="pedidos",
    )

    situacao = models.CharField(
        max_length=10,
        choices=[
            ("recebido", "Recebido"),
            ("separado", "Separado"),
            ("entregue", "Entregue"),
            ("cancelado", "Cancelado"),
        ],
        default="recebido",
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido {self.id} - {self.comprador}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens",
    )

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
    )

    nome_produto = models.CharField(max_length=150)
    nome_produtor = models.CharField(max_length=150)
    nome_unidade = models.CharField(max_length=100)

    preco_unitario_centavos = models.PositiveIntegerField()

    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=3,
    )

    def __str__(self):
        return f"{self.quantidade} x {self.nome_produto}"
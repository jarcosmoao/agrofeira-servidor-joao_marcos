from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest import mock
from django.db import transaction
from catalogo.models import Categoria, Produto, Produtor, Unidade
from pedidos import servicos
from pedidos.carrinho import subtotal_centavos
from pedidos.models import Pedido, PontoRetirada
from pedidos.forms import AdicionarAoCarrinhoForm
from django.urls import reverse


class BaseDeTeste(TestCase):
    """Os dados que as classes de teste de pedidos usam."""

    @classmethod
    def setUpTestData(cls):
        categoria = Categoria.objects.create(
            nome="Hortaliças",
            slug="hortalicas"
        )

        maco = Unidade.objects.create(
            nome="maço",
            sigla="maço",
            fracionavel=False
        )

        quilo = Unidade.objects.create(
            nome="quilo",
            sigla="kg",
            fracionavel=True
        )

        sousa = Produtor.objects.create(
            nome="Irmãos Sousa",
            slug="irmaos-sousa",
            caf="A1",
            pedido_minimo_centavos=1000,
        )

        tonico = Produtor.objects.create(
            nome="Seu Tonico",
            slug="seu-tonico",
            caf="A2",
            pedido_minimo_centavos=2000,
        )

        cls.jambu = Produto.objects.create(
            nome="Jambu",
            slug="jambu",
            categoria=categoria,
            produtor=sousa,
            unidade=maco,
            preco_centavos=400,
            estoque=Decimal("50"),
        )

        cls.cheiro = Produto.objects.create(
            nome="Cheiro-verde",
            slug="cheiro-verde",
            categoria=categoria,
            produtor=sousa,
            unidade=maco,
            preco_centavos=300,
            estoque=Decimal("40"),
        )

        cls.farinha = Produto.objects.create(
            nome="Farinha seca",
            slug="farinha-seca",
            categoria=categoria,
            produtor=tonico,
            unidade=quilo,
            preco_centavos=1000,
            estoque=Decimal("60"),
        )

        cls.ponto = PontoRetirada.objects.create(
            nome="Feira do Centro",
            endereco="Praça central",
            horario="sábado, 7h"
        )

        cls.dados = {
            "comprador": "Maria",
            "telefone": "(91) 90000-0000",
            "ponto_retirada": cls.ponto,
        }


class SubtotalTests(TestCase):

    def test_preco_vezes_quantidade_inteira(self):
        self.assertEqual(subtotal_centavos(400, Decimal("3")), 1200)

    def test_quantidade_quebrada(self):
        self.assertEqual(subtotal_centavos(1000, Decimal("1.5")), 1500)

    def test_arredonda_meio_centavo_para_cima(self):
        # 333 x 1,5 = 499,5 centavos, que arredondam para 500
        self.assertEqual(subtotal_centavos(333, Decimal("1.5")), 500)


class ValidarQuantidadeTests(BaseDeTeste):

    def test_aceita_inteiro_em_unidade_inteira(self):
        servicos.validar_quantidade(self.jambu, Decimal("2"))

    def test_aceita_quebrado_em_unidade_fracionavel(self):
        servicos.validar_quantidade(self.farinha, Decimal("1.5"))

    def test_aceita_exatamente_o_estoque(self):
        servicos.validar_quantidade(self.jambu, Decimal("50"))

    def test_recusa_quebrado_em_unidade_inteira(self):
        with self.assertRaises(ValidationError):
            servicos.validar_quantidade(self.jambu, Decimal("1.5"))

    def test_recusa_zero_e_negativo(self):
        for quantidade in ("0", "-1"):
            with self.subTest(quantidade=quantidade):
                with self.assertRaises(ValidationError):
                    servicos.validar_quantidade(
                        self.jambu,
                        Decimal(quantidade)
                    )

    def test_recusa_mais_do_que_o_estoque(self):
        with self.assertRaises(ValidationError):
            servicos.validar_quantidade(self.jambu, Decimal("51"))

class AdicionarAoCarrinhoFormTests(BaseDeTeste):

    def test_quantidade_valida(self):
        form = AdicionarAoCarrinhoForm(
            {"quantidade": "2"},
            produto=self.jambu
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["quantidade"], Decimal("2"))

    def test_texto_que_nao_e_numero(self):
        form = AdicionarAoCarrinhoForm(
            {"quantidade": "muito"},
            produto=self.jambu
        )
        self.assertFalse(form.is_valid())
        self.assertIn("quantidade", form.errors)

    def test_quebrada_em_unidade_inteira_vira_erro_do_formulario(self):
        form = AdicionarAoCarrinhoForm(
            {"quantidade": "1.5"},
            produto=self.jambu
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "quantidade quebrada",
            form.non_field_errors()[0]
        )

class CriarPedidoTests(BaseDeTeste):

    def test_pedido_abaixo_do_minimo_do_produtor_e_recusado(self):
        # 2 maços de jambu = R$ 8,00; mínimo dos Irmãos Sousa = R$ 10,00
        with self.assertRaises(ValidationError) as contexto:
            servicos.criar_pedido({str(self.jambu.pk): "2"}, self.dados)

        mensagem = contexto.exception.messages[0]
        self.assertIn("Irmãos Sousa", mensagem)
        self.assertIn("2,00", mensagem)  # faltam R$ 2,00
        self.assertEqual(Pedido.objects.count(), 0)

    def test_o_minimo_soma_os_itens_do_mesmo_produtor(self):
        # Jambu (R$ 8,00) + cheiro-verde (R$ 3,00) = R$ 11,00
        carrinho = {
            str(self.jambu.pk): "2",
            str(self.cheiro.pk): "1",
        }

        pedido = servicos.criar_pedido(carrinho, self.dados)
        self.assertEqual(pedido.itens.count(), 2)

def criar_duas_categorias():
    """Função de brinquedo, só para ensaiar a transação: grava as duas
    categorias, ou nenhuma."""
    with transaction.atomic():
        Categoria.objects.create(nome="Frutas", slug="frutas")
        Categoria.objects.create(nome="Raízes", slug="raizes")

class TransacaoDeBrinquedoTests(TestCase):
    def test_falha_na_segunda_nao_deixa_a_primeira(self):
        cria_de_verdade = Categoria.objects.create
        chamadas = []

        def cria_a_primeira_e_falha_na_segunda(**campos):
            chamadas.append(campos)
            if len(chamadas) == 2:
                raise RuntimeError("falha plantada")
            return cria_de_verdade(**campos)

        with mock.patch.object(
            Categoria.objects, "create",
            side_effect=cria_a_primeira_e_falha_na_segunda
        ):
            with self.assertRaises(RuntimeError):
                criar_duas_categorias()

        self.assertEqual(Categoria.objects.count(), 0)

class CarrinhoPaginasTests(BaseDeTeste):
    def test_pagina_do_produto_traz_o_formulario(self):
        resposta = self.client.get(
            reverse("catalogo:produto", args=["jambu"])
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(
            resposta, "catalogo/produto_detalhe.html"
        )
        self.assertIn("form", resposta.context)

    def test_slug_inexistente_e_404(self):
        resposta = self.client.get(
            reverse("catalogo:produto", args=["nao-existe"])
        )
        self.assertEqual(resposta.status_code, 404)

    def test_adicionar_redireciona_para_o_carrinho_e_guarda_na_sessao(self):
        resposta = self.client.post(
            reverse("catalogo:produto", args=["jambu"]),
            {"quantidade": "2"}
        )

        self.assertRedirects(
            resposta,
            reverse("pedidos:carrinho")
        )
        self.assertEqual(
            self.client.session["carrinho"],
            {str(self.jambu.pk): "2"}
        )

    def test_a_mensagem_aparece_na_pagina_seguinte(self):
        resposta = self.client.post(
            reverse("catalogo:produto", args=["jambu"]),
            {"quantidade": "2"},
            follow=True
        )

        self.assertContains(resposta, "Jambu entrou no carrinho.")

    def test_quantidade_quebrada_volta_com_erro_e_nao_guarda(self):
        resposta = self.client.post(
            reverse("catalogo:produto", args=["jambu"]),
            {"quantidade": "1.5"}
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "quantidade quebrada")
        self.assertNotIn("carrinho", self.client.session)

    def test_o_preco_forjado_no_envio_nao_muda_o_subtotal(self):
        self.client.post(
            reverse("catalogo:produto", args=["jambu"]),
            {"quantidade": "2", "preco": "1"}
        )

        resposta = self.client.get(
            reverse("pedidos:carrinho")
        )

        self.assertContains(resposta, "R$ 8,00")

    def test_carrinho_vazio_mostra_o_aviso(self):
        resposta = self.client.get(
            reverse("pedidos:carrinho")
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Seu carrinho está vazio.")

    def test_esvaziar_so_aceita_post(self):
        resposta = self.client.get(
            reverse("pedidos:esvaziar")
        )

        self.assertEqual(resposta.status_code, 405)

    def test_sem_token_csrf_o_envio_e_recusado(self):
        cliente = self.client_class(enforce_csrf_checks=True)

        resposta = cliente.post(
            reverse("catalogo:produto", args=["jambu"]),
            {"quantidade": "2"}
        )

        self.assertEqual(resposta.status_code, 403)
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from catalogo.models import (
    Categoria,
    JanelaSafra,
    Produto,
    Produtor,
    Unidade,
)


class CatalogoBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.frutas = Categoria.objects.create(
            nome="Frutas",
            slug="frutas",
        )

        cls.quilo = Unidade.objects.create(
            nome="Quilo",
            sigla="kg",
            fracionavel=True,
        )

        cls.produtor = Produtor.objects.create(
            nome="Família Oliveira",
            slug="familia-oliveira",
            comunidade="Comunidade do Campo",
            caf="B1",
            formas_pagamento="Pix",
            chave_pix="chave-teste",
        )

        cls.cupuacu = Produto.objects.create(
            nome="Cupuaçu",
            slug="cupuacu",
            categoria=cls.frutas,
            produtor=cls.produtor,
            unidade=cls.quilo,
            preco_centavos=1200,
            estoque=Decimal("20"),
        )

        cls.banana = Produto.objects.create(
            nome="Banana",
            slug="banana",
            categoria=cls.frutas,
            produtor=cls.produtor,
            unidade=cls.quilo,
            preco_centavos=500,
            estoque=Decimal("30"),
        )

        cls.janela_cupuacu = JanelaSafra.objects.create(
            produto=cls.cupuacu,
            mes_inicio=3,
            mes_fim=8,
            situacao="pico",
        )

        cls.janela_banana = JanelaSafra.objects.create(
            produto=cls.banana,
            mes_inicio=1,
            mes_fim=12,
            situacao="disponivel",
        )


class JanelaSafraTests(CatalogoBase):
    def test_o_texto_da_janela(self):
        self.assertEqual(
            str(self.janela_cupuacu),
            "março a agosto: pico de safra",
        )


class DisponiveisEmTests(CatalogoBase):
    def test_dentro_da_janela_inclusive_nos_extremos(self):
        for mes in (3, 5, 8):
            with self.subTest(mes=mes):
                self.assertIn(
                    self.cupuacu,
                    Produto.objects.disponiveis_em(mes),
                )

    def test_fora_da_janela(self):
        for mes in (1, 2, 9, 12):
            with self.subTest(mes=mes):
                self.assertNotIn(
                    self.cupuacu,
                    Produto.objects.disponiveis_em(mes),
                )

    def test_janela_do_ano_inteiro_vale_em_qualquer_mes(self):
        for mes in (1, 6, 12):
            with self.subTest(mes=mes):
                self.assertIn(
                    self.banana,
                    Produto.objects.disponiveis_em(mes),
                )

    def test_entressafra_nao_conta_como_disponivel(self):
        self.janela_cupuacu.situacao = "entressafra"
        self.janela_cupuacu.save()

        self.assertNotIn(
            self.cupuacu,
            Produto.objects.disponiveis_em(5),
        )


class PaginasTests(CatalogoBase):
    def test_home_abre(self):
        resposta = self.client.get(reverse("catalogo:inicio"))

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "catalogo/home.html")

    def test_lista_de_produtos(self):
        resposta = self.client.get(
            reverse("catalogo:produtos")
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Cupuaçu")
        self.assertContains(resposta, "Banana")

    def test_busca_filtra_produtos(self):
        resposta = self.client.get(
            reverse("catalogo:produtos"),
            {"q": "cupu"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Cupuaçu")
        self.assertNotContains(resposta, "Banana")

    def test_detalhe_do_produto(self):
        resposta = self.client.get(
            reverse(
                "catalogo:produto",
                args=["cupuacu"],
            )
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.context["produto"],
            self.cupuacu,
        )

class SafraQueAtravessaOAnoTests(CatalogoBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.cupuacu_virando = Produto.objects.create(
            nome="Cupuaçu de inverno",
            slug="cupuacu-de-inverno",
            categoria=cls.frutas,
            produtor=cls.produtor,
            unidade=cls.quilo,
            preco_centavos=1500,
            estoque=Decimal("10"),
        )

        cls.safra_virando = JanelaSafra.objects.create(
            produto=cls.cupuacu_virando,
            mes_inicio=11,
            mes_fim=2,
            situacao="pico",
        )

        cls.cupuacu_dezembro = Produto.objects.create(
            nome="Cupuaçu de dezembro",
            slug="cupuacu-de-dezembro",
            categoria=cls.frutas,
            produtor=cls.produtor,
            unidade=cls.quilo,
            preco_centavos=1800,
            estoque=Decimal("10"),
        )

        cls.safra_dezembro = JanelaSafra.objects.create(
            produto=cls.cupuacu_dezembro,
            mes_inicio=12,
            mes_fim=12,
            situacao="disponivel",
        )

    def test_safra_que_vira_o_ano(self):
        for mes in (11, 12, 1, 2):
            with self.subTest(mes=mes):
                self.assertIn(
                    self.cupuacu_virando,
                    Produto.objects.disponiveis_em(mes),
                )

        for mes in (3, 6, 10):
            with self.subTest(mes=mes):
                self.assertNotIn(
                    self.cupuacu_virando,
                    Produto.objects.disponiveis_em(mes),
                )

    def test_janela_de_um_mes_so_vale_naquele_mes(self):
        for mes in (12,):
            with self.subTest(mes=mes):
                self.assertIn(
                    self.cupuacu_dezembro,
                    Produto.objects.disponiveis_em(mes),
                )

        for mes in (11, 1):
            with self.subTest(mes=mes):
                self.assertNotIn(
                    self.cupuacu_dezembro,
                    Produto.objects.disponiveis_em(mes),
                )
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from agrofeira.middleware import TempoDeRespostaMiddleware


SESSAO = "django.contrib.sessions.middleware.SessionMiddleware"
MENSAGENS = "django.contrib.messages.middleware.MessageMiddleware"
TEMPO = "agrofeira.middleware.TempoDeRespostaMiddleware"


class OrdemDoMiddlewareTests(TestCase):

    @override_settings(MIDDLEWARE=[SESSAO, MENSAGENS])
    def test_sessao_antes_das_mensagens_funciona(self):
        resposta = self.client.get("/produtos/")
        self.assertEqual(resposta.status_code, 200)

    @override_settings(MIDDLEWARE=[MENSAGENS, SESSAO])
    def test_mensagens_antes_da_sessao_quebra(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.get("/produtos/")


class TempoDeRespostaTests(TestCase):

    @override_settings(MIDDLEWARE=[TEMPO])
    def test_resposta_de_produtos_tem_cabecalho(self):
        resposta = self.client.get("/produtos/")

        self.assertIn("X-Tempo-Resposta", resposta.headers)
        self.assertTrue(
            resposta.headers["X-Tempo-Resposta"].endswith("ms")
        )

    @override_settings(MIDDLEWARE=[TEMPO])
    def test_resposta_404_tambem_tem_cabecalho(self):
        resposta = self.client.get("/endereco-que-nao-existe/")

        self.assertEqual(resposta.status_code, 404)
        self.assertIn("X-Tempo-Resposta", resposta.headers)
        self.assertTrue(
            resposta.headers["X-Tempo-Resposta"].endswith("ms")
        )


class TempoDeRespostaLigadoTests(TestCase):

    def test_middleware_esta_ligado_no_projeto(self):
        resposta = self.client.get("/produtos/")

        self.assertIn("X-Tempo-Resposta", resposta.headers)
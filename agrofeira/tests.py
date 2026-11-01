from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings


SESSAO = "django.contrib.sessions.middleware.SessionMiddleware"
MENSAGENS = "django.contrib.messages.middleware.MessageMiddleware"


class OrdemDoMiddlewareTests(TestCase):

    @override_settings(MIDDLEWARE=[SESSAO, MENSAGENS])
    def test_sessao_antes_das_mensagens_funciona(self):
        resposta = self.client.get("/produtos/")
        self.assertEqual(resposta.status_code, 200)

    @override_settings(MIDDLEWARE=[MENSAGENS, SESSAO])
    def test_mensagens_antes_da_sessao_quebra(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.get("/produtos/")
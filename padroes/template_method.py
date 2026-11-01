class Relatorio:
    def gerar(self):
        linhas = [
            self.titulo(),
            *self.corpo(),
            "--- fim ---"
        ]
        return "\n".join(linhas)

    def titulo(self):
        return "RELATÓRIO"

    def corpo(self):
        raise NotImplementedError


class RelatorioDeEstoque(Relatorio):
    def titulo(self):
        return "ESTOQUE"

    def corpo(self):
        return ["jambu: 50", "farinha: 60"]


print(RelatorioDeEstoque().gerar())
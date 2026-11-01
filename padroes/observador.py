class Estoque:
    def __init__(self):
        self.ouvintes = []

    def inscrever(self, funcao):
        self.ouvintes.append(funcao)

    def baixar(self, quantidade):
        print("baixou", quantidade)
        for ouvinte in self.ouvintes:
            ouvinte(quantidade)


estoque = Estoque()

estoque.inscrever(
    lambda q: print("avisar o produtor:", q)
)

estoque.inscrever(
    lambda q: print("registrar no diário:", q)
)

estoque.baixar(3)
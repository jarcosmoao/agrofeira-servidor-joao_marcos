class Dobrar:
    def __init__(self, fator):
        self.fator = fator

    def __call__(self, numero):
        return numero * self.fator


dobro = Dobrar(2)

print(dobro(21))
print(callable(dobro), callable(len), callable(42))
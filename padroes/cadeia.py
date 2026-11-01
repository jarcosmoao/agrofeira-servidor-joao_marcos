def final(texto):
    print("    o miolo recebeu:", texto)
    return texto.upper()


def elo(nome, proximo):
    def chamar(texto):
        print(f"{nome} entra com {texto!r}")
        resposta = proximo(texto + nome)
        print(f"{nome} sai com {resposta!r}")
        return resposta

    return chamar


cadeia = elo("A", elo("B", final))
print(cadeia("x"))
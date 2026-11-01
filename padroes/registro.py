FORMATOS = {}


def registrar(nome, funcao):
    FORMATOS[nome] = funcao


def em_csv(linhas):
    return "\n".join(",".join(linha) for linha in linhas)


def em_texto(linhas):
    return "\n".join(" ".join(linha) for linha in linhas)


registrar("csv", em_csv)
registrar("texto", em_texto)

dados = [["jambu", "4"], ["farinha", "10"]]

for nome in FORMATOS:
    print(
        nome,
        "->",
        FORMATOS[nome](dados).replace("\n", " | ")
    )
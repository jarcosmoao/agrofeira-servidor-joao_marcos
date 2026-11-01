import sqlite3

banco = sqlite3.connect(":memory:")
banco.execute("create table nota (id integer primary key, texto text)")


class Nota:
    def __init__(self, texto, id=None):
        self.texto = texto
        self.id = id

    def salvar(self):
        if self.id is None:
            cursor = banco.execute(
                "insert into nota (texto) values (?)",
                (self.texto,)
            )
            self.id = cursor.lastrowid
        else:
            banco.execute(
                "update nota set texto = ? where id = ?",
                (self.texto, self.id)
            )

    @classmethod
    def buscar(cls, id):
        (texto,) = banco.execute(
            "select texto from nota where id = ?",
            (id,)
        ).fetchone()

        return cls(texto, id)


nota = Nota("comprar farinha")
nota.salvar()
print(nota.id)

nota.texto = "comprar farinha e jambu"
nota.salvar()
print(Nota.buscar(1).texto)
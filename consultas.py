from catalogo.models import Produto, Produtor, Categoria
from django.db.models import Q, F, Count, Sum
from django.db import connection

# 1. Produtos de até R$ 10,00, do mais barato para o mais caro.
c1 = Produto.objects.filter(
    preco_centavos__lte=1000
).order_by("preco_centavos")

print(1, list(c1))
# SQL: SELECT "catalogo_produto"."id", "catalogo_produto"."nome", "catalogo_produto"."slug", "catalogo_produto"."variedade", "catalogo_produto"."descricao", "catalogo_produto"."categoria_id", "catalogo_produto"."produtor_id", "catalogo_produto"."propriedade_id", "catalogo_produto"."unidade_id", "catalogo_produto"."preco_centavos", "catalogo_produto"."estoque", "catalogo_produto"."destaque", "catalogo_produto"."conservacao", "catalogo_produto"."validade" FROM "catalogo_produto" WHERE "catalogo_produto"."preco_centavos" <= 1000 ORDER BY "catalogo_produto"."preco_centavos" ASC
print("SQL 1:", c1.query)

# 2. Produtos com "farinha" ou "tapioca" no nome.
c2 = Produto.objects.filter(
    Q(nome__icontains="farinha") | Q(nome__icontains="tapioca")
)

print(2, list(c2))
# SQL: SELECT "catalogo_produto"."id", "catalogo_produto"."nome", "catalogo_produto"."slug", "catalogo_produto"."variedade", "catalogo_produto"."descricao", "catalogo_produto"."categoria_id", "catalogo_produto"."produtor_id", "catalogo_produto"."propriedade_id", "catalogo_produto"."unidade_id", "catalogo_produto"."preco_centavos", "catalogo_produto"."estoque", "catalogo_produto"."destaque", "catalogo_produto"."conservacao", "catalogo_produto"."validade" FROM "catalogo_produto" WHERE ("catalogo_produto"."nome" LIKE %farinha% ESCAPE '\' OR "catalogo_produto"."nome" LIKE %tapioca% ESCAPE '\') ORDER BY "catalogo_produto"."nome" ASC
print("SQL 2:", c2.query)

# 3. Produtos dos produtores da comunidade Colônia do Uraim.
c3 = Produto.objects.filter(
    produtor__comunidade="Colônia do Uraim"
)

print(3, list(c3))
# SQL: SELECT "catalogo_produto"."id", "catalogo_produto"."nome", "catalogo_produto"."slug", "catalogo_produto"."variedade", "catalogo_produto"."descricao", "catalogo_produto"."categoria_id", "catalogo_produto"."produtor_id", "catalogo_produto"."propriedade_id", "catalogo_produto"."unidade_id", "catalogo_produto"."preco_centavos", "catalogo_produto"."estoque", "catalogo_produto"."destaque", "catalogo_produto"."conservacao", "catalogo_produto"."validade" FROM "catalogo_produto" INNER JOIN "catalogo_produtor" ON ("catalogo_produto"."produtor_id" = "catalogo_produtor"."id") WHERE "catalogo_produtor"."comunidade" = Colônia do Uraim ORDER BY "catalogo_produto"."nome" ASC
print("SQL 3:", c3.query)

# 4. Produtos vendidos em unidades fracionáveis.
c4 = Produto.objects.filter(unidade__fracionavel=True)

print(4, list(c4))
# SQL: SELECT "catalogo_produto"."id", "catalogo_produto"."nome", "catalogo_produto"."slug", "catalogo_produto"."variedade", "catalogo_produto"."descricao", "catalogo_produto"."categoria_id", "catalogo_produto"."produtor_id", "catalogo_produto"."propriedade_id", "catalogo_produto"."unidade_id", "catalogo_produto"."preco_centavos", "catalogo_produto"."estoque", "catalogo_produto"."destaque", "catalogo_produto"."conservacao", "catalogo_produto"."validade" FROM "catalogo_produto" INNER JOIN "catalogo_unidade" ON ("catalogo_produto"."unidade_id" = "catalogo_unidade"."id") WHERE "catalogo_unidade"."fracionavel" = True ORDER BY "catalogo_produto"."nome" ASC
print("SQL 4:", c4.query)

# 5. Produtores independentes, sem cooperativa.
c5 = Produtor.objects.filter(cooperativa="")

print(5, list(c5))
# SQL: SELECT "catalogo_produtor"."id", "catalogo_produtor"."nome", "catalogo_produtor"."slug", "catalogo_produtor"."comunidade", "catalogo_produtor"."descricao", "catalogo_produtor"."caf", "catalogo_produtor"."cooperativa", "catalogo_produtor"."formas_pagamento", "catalogo_produtor"."chave_pix", "catalogo_produtor"."pedido_minimo_centavos" FROM "catalogo_produtor" WHERE "catalogo_produtor"."cooperativa" =  ORDER BY "catalogo_produtor"."nome" ASC
print("SQL 5:", c5.query)

# 6. Estoque total de cada produtor, do maior para o menor.
c6 = Produtor.objects.annotate(
    estoque_total=Sum("produtos__estoque")
).order_by("-estoque_total")

print(6, list(c6.values_list("nome", "estoque_total")))
# SQL: SELECT "catalogo_produtor"."id", "catalogo_produtor"."nome", "catalogo_produtor"."slug", "catalogo_produtor"."comunidade", "catalogo_produtor"."descricao", "catalogo_produtor"."caf", "catalogo_produtor"."cooperativa", "catalogo_produtor"."formas_pagamento", "catalogo_produtor"."chave_pix", "catalogo_produtor"."pedido_minimo_centavos", SUM("catalogo_produto"."estoque") AS "estoque_total" FROM "catalogo_produtor" LEFT OUTER JOIN "catalogo_produto" ON ("catalogo_produtor"."id" = "catalogo_produto"."produtor_id") GROUP BY "catalogo_produtor"."id", "catalogo_produtor"."nome", "catalogo_produtor"."slug", "catalogo_produtor"."comunidade", "catalogo_produtor"."descricao", "catalogo_produtor"."caf", "catalogo_produtor"."cooperativa", "catalogo_produtor"."formas_pagamento", "catalogo_produtor"."chave_pix", "catalogo_produtor"."pedido_minimo_centavos" ORDER BY 11 DESC
print("SQL 6:", c6.query)

# 7. Quantidade e estoque total da categoria Hortaliças e temperos verdes.
c7 = Categoria.objects.filter(
    nome="Hortaliças e temperos verdes"
).annotate(
    quantidade=Count("produtos"),
    estoque_total=Sum("produtos__estoque")
)

print(7, list(c7.values("nome", "quantidade", "estoque_total")))
# SQL: SELECT "catalogo_categoria"."id", "catalogo_categoria"."nome", "catalogo_categoria"."slug", COUNT("catalogo_produto"."id") AS "quantidade", SUM("catalogo_produto"."estoque") AS "estoque_total" FROM "catalogo_categoria" LEFT OUTER JOIN "catalogo_produto" ON ("catalogo_categoria"."id" = "catalogo_produto"."categoria_id") WHERE "catalogo_categoria"."nome" = Hortaliças e temperos verdes GROUP BY "catalogo_categoria"."id", "catalogo_categoria"."nome", "catalogo_categoria"."slug"
print("SQL 7:", c7.query)

# 8. Valor total de todo o estoque da feira, em centavos.
c8 = Produto.objects.aggregate(
    valor_total=Sum(F("preco_centavos") * F("estoque"))
)

print(8, c8["valor_total"])
# SQL: SELECT SUM(("catalogo_produto"."preco_centavos" * "catalogo_produto"."estoque")) AS "valor_total" FROM "catalogo_produto"
print("SQL 8:", connection.queries[-1]["sql"])

# 9. Produtores sem nenhum produto disponível em abril.
c9 = Produtor.objects.exclude(
    pk__in=Produto.objects.disponiveis_em(4).values("produtor_id")
)

print(9, list(c9))
# SQL: SELECT "catalogo_produtor"."id", "catalogo_produtor"."nome", "catalogo_produtor"."slug", "catalogo_produtor"."comunidade", "catalogo_produtor"."descricao", "catalogo_produtor"."caf", "catalogo_produtor"."cooperativa", "catalogo_produtor"."formas_pagamento", "catalogo_produtor"."chave_pix", "catalogo_produtor"."pedido_minimo_centavos" FROM "catalogo_produtor" WHERE NOT ("catalogo_produtor"."id" IN (SELECT DISTINCT "U0"."produtor_id" AS "produtor_id" FROM "catalogo_produto" "U0" INNER JOIN "catalogo_janelasafra" "U1" ON ("U0"."id" = "U1"."produto_id") WHERE ((("U1"."mes_fim" >= 4 AND "U1"."mes_inicio" <= 4) OR ("U1"."mes_inicio" > ("U1"."mes_fim") AND ("U1"."mes_inicio" <= 4 OR "U1"."mes_fim" >= 4))) AND "U1"."situacao" IN (pico, disponivel)))) ORDER BY "catalogo_produtor"."nome" ASC
print("SQL 9:", c9.query)

# 10. Produtos de produtores independentes disponíveis em fevereiro.
c10 = Produto.objects.filter(
    produtor__cooperativa=""
).disponiveis_em(2).order_by(
    "preco_centavos", "nome"
)

print(10, list(c10))
# SQL: SELECT DISTINCT "catalogo_produto"."id", "catalogo_produto"."nome", "catalogo_produto"."slug", "catalogo_produto"."variedade", "catalogo_produto"."descricao", "catalogo_produto"."categoria_id", "catalogo_produto"."produtor_id", "catalogo_produto"."propriedade_id", "catalogo_produto"."unidade_id", "catalogo_produto"."preco_centavos", "catalogo_produto"."estoque", "catalogo_produto"."destaque", "catalogo_produto"."conservacao", "catalogo_produto"."validade" FROM "catalogo_produto" INNER JOIN "catalogo_produtor" ON ("catalogo_produto"."produtor_id" = "catalogo_produtor"."id") INNER JOIN "catalogo_janelasafra" ON ("catalogo_produto"."id" = "catalogo_janelasafra"."produto_id") WHERE ("catalogo_produtor"."cooperativa" =  AND (("catalogo_janelasafra"."mes_fim" >= 2 AND "catalogo_janelasafra"."mes_inicio" <= 2) OR ("catalogo_janelasafra"."mes_inicio" > ("catalogo_janelasafra"."mes_fim") AND ("catalogo_janelasafra"."mes_inicio" <= 2 OR "catalogo_janelasafra"."mes_fim" >= 2))) AND "catalogo_janelasafra"."situacao" IN (pico, disponivel)) ORDER BY "catalogo_produto"."preco_centavos" ASC, "catalogo_produto"."nome" ASC
print("SQL 10:", c10.query)

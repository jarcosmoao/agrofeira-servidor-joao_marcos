from django.urls import path
from . import views

app_name = "catalogo"

urlpatterns = [
    path("", views.home, name="inicio"),
    path("produtos/", views.produtos, name="produtos"),
    path("produtos/<slug:slug>/", views.produto, name="produto"),
    path("produtores/", views.produtores, name="produtores"),
    path("produtores/<slug:slug>/", views.produtor, name="produtor"),
]
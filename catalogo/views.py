from django.http import HttpResponse


def inicio(request):
    return HttpResponse("<h1>AgroFeira Paragominas</h1>")
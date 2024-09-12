from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "index.html")


def usuarios(request):
    return render(request, "user/usuarios.html")


def first_login(request):
    return render(request, "login/login.html")


def alleleviewer(request):
    return render(request, "grafico/alleleviewer.html")


def uploadfile(request):
    return render(request, "grafico/uploadfile.html")


def mapgeneral(request):
    return render(request, "map/mapgeneral.html")


def register(request):
    return render(request, "login/register.html")

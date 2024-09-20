from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "index.html")


def usuarios(request):
    return render(request, "user/usuarios.html")


def first_login(request):
    return render(request, "login/login.html")


def register(request):
    return render(request, "login/register.html")
    
def brands(request):
    return render(request, "brands/brands.html")
def models(request):
    return render(request, "models/models.html")

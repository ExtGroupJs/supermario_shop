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


def shops(request):
    return render(request, "shops/shop.html")


def products(request):
    return render(request, "products/products.html")
def catalogo(request):
    return render(request, "catalogo/catalogo.html")


def shop_products(request):
    return render(request, "shop_products/shop_products.html")


def sales_products(request):
    return render(request, "sales_products/sales_products.html")


def sales(request):
    return render(request, "sales/sales.html")


def salescar(request):
    return render(request, "sales_products/salescar.html")
def dashboard(request):
    return render(request, "dashboard/dashboard.html")

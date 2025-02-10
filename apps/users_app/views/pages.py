from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test

from apps.users_app.models.groups import Groups


# Create your views here.


def is_owner(user):
    return user.groups.filter(id=Groups.SHOP_OWNER.value).exists()


def index(request):
    return render(request, "index.html")


@user_passes_test(is_owner)
def usuarios(request):
    return render(request, "user/usuarios.html")


def first_login(request):
    return render(request, "login/login.html")


@user_passes_test(is_owner)
def register(request):
    return render(request, "login/register.html")


@user_passes_test(is_owner)
def brands(request):
    return render(request, "brands/brands.html")

@user_passes_test(is_owner)
def clients(request):
    return render(request, "clients/clients.html")


@user_passes_test(is_owner)
def models(request):
    return render(request, "models/models.html")


@user_passes_test(is_owner)
def shops(request):
    return render(request, "shops/shop.html")


@user_passes_test(is_owner)
def products(request):
    return render(request, "products/products.html")


@user_passes_test(is_owner)
def create_products(request):
    return render(request, "products/create_products.html")


def catalog(request):
    return render(request, "catalogo/catalogo.html")


@user_passes_test(is_owner)
def shop_products(request):
    return render(request, "shop_products/shop_products.html")


@user_passes_test(is_owner)
def create_shop_products(request):
    return render(request, "shop_products/create_shop_products.html")


def inventario(request):
    return render(request, "inventario/inventario.html")


def inventario_entrada_log(request):
    return render(request, "inventario/inventario_entrada_log.html")


def sales_products(request):
    return render(request, "sales_products/sales_products.html")


@user_passes_test(is_owner)
def sales(request):
    return render(request, "sales/sales.html")


def sales_tienda(request):
    return render(request, "sales/sales_tienda.html")


def salescar(request):
    return render(request, "sales_products/salescar.html")


@user_passes_test(is_owner)
def dashboard(request):
    return render(request, "dashboard/dashboard.html")


def user_redirect(request):
    if request.user.groups.filter(id=Groups.SHOP_OWNER.value).exists():
        return redirect("dashboard")
    else:
        return redirect("sales_tienda")

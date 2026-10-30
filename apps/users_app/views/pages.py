from functools import wraps

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test

from apps.common.utils.geo import get_country_code
from apps.users_app.models.groups import Groups
from apps.business_app.models.shop import Shop


# Create your views here.

CUBA = "CU"


def catalog_visible(view):
    """Allow public catalog pages to logged users and visitors from abroad."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            country = get_country_code(request)
            if country in ("", CUBA):
                return redirect("first_login")
        return view(request, *args, **kwargs)

    return wrapper


def is_owner(user):
    return user.groups.filter(id=Groups.SHOP_OWNER.value).exists()


def index(request):
    return render(request, "index.html")


def _get_catalog_context():
    principal_shop = (
        Shop.objects.filter(principal=True, enabled=True)
        .exclude(catalog_url__isnull=True)
        .exclude(catalog_url__exact="")
        .first()
    )
    return {
        "catalog_shop_url": principal_shop.catalog_url if principal_shop else "",
    }


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


@catalog_visible
def catalog(request):
    return render(request, "catalogo/catalogo.html", _get_catalog_context())


@catalog_visible
def root_catalog(request):
    return render(request, "catalogo/catalogo.html", _get_catalog_context())


def catalog_by_shop(request, catalog_url):
    return render(request, "catalogo/catalogo.html", {"catalog_shop_url": catalog_url})


@catalog_visible
def wholesale_catalog(request):
    return render(request, "catalogo_por_mayor/catalogo_por_mayor.html")


@user_passes_test(is_owner)
def shop_products(request):
    return render(request, "shop_products/shop_products.html")


@user_passes_test(is_owner)
def shop_products_auto(request):
    return render(request, "shop_products/create_shop_products_auto.html")


@user_passes_test(is_owner)
def create_sales_auto(request):
    return render(request, "sales/create_sales_auto.html")


@user_passes_test(is_owner)
def shop_products_move_auto(request):
    return render(request, "shop_products/move_shop_products_auto.html")


@user_passes_test(is_owner)
def shop_products_move_auto_movil(request):
    return render(request, "movil/shop_products/move_shop_products_auto_movil.html")


@user_passes_test(is_owner)
def shop_products_auto_movil(request):
    return render(request, "movil/shop_products/create_shop_products_auto_movil.html")


@user_passes_test(is_owner)
def create_sales_auto_movil(request):
    return render(request, "movil/sales/create_sales_auto_movil.html")


@user_passes_test(is_owner)
def edit_product_image_movil(request):
    return render(request, "movil/products/edit_product_image_movil.html")


@user_passes_test(is_owner)
def create_shop_products(request):
    return render(request, "shop_products/create_shop_products.html")


@user_passes_test(is_owner)
def pallets(request):
    return render(request, "pallets/pallets.html")


@user_passes_test(is_owner)
def pallet_detail(request, pallet_id):
    return render(request, "pallets/pallet_detail.html", {"pallet_id": pallet_id})


def inventario(request):
    return render(request, "inventario/inventario.html")


def inventario_entrada_log(request):
    return render(request, "inventario/inventario_entrada_log.html")


def sales_products(request):
    return render(request, "sales_products/sales_products.html")


@user_passes_test(is_owner)
def sales(request):
    return render(request, "sales/sales.html")


@user_passes_test(is_owner)
def group_sells(request):
    # The delete button is shown only to admins/owners: sellers never reach
    # this page today, but the flag keeps the action tied to the same roles
    # the API would accept a destroy from.
    can_delete = request.user.is_superuser or request.user.groups.filter(
        id__in=[Groups.SUPER_ADMIN.value, Groups.SHOP_OWNER.value]
    ).exists()
    return render(request, "sales/group_sells.html", {"can_delete_group": can_delete})


@user_passes_test(is_owner)
def inputs(request):
    return render(request, "input/input.html")


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

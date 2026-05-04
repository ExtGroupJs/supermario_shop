"""
Tests para la migración 0023 que corrige Brand y Model invertidos en 0022.

Esta migración fue diseñada para reparar una inversión accidental donde
los campos model_name y brand_name fueron intercambiados durante la
población inicial de datos en la tienda Tecnología Ciego (Onel).
"""

import importlib

import pytest
from django.apps import apps as django_apps
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from apps.business_app.models.brand import Brand
from apps.business_app.models.model import Model
from apps.business_app.models.product import Product
from apps.business_app.models.shop import Shop
from apps.business_app.models.shop_products import ShopProducts


MIGRATION_MODULE = importlib.import_module(
    "apps.business_app.migrations.0023_fix_swapped_brand_model_onel_shop"
)


def _build_logo_file(filename):
    """Crea un archivo fake para logos de tienda."""
    return SimpleUploadedFile(
        filename, b"fake-image-content", content_type="image/jpeg"
    )


def _get_or_create_shop(name, shop_type=Shop.TYPE_CHOICES.TECH):
    """Obtiene o crea una tienda con el tipo especificado."""
    existing_shop = Shop.objects.filter(name=name).first()
    if existing_shop:
        return existing_shop
    return baker.make(
        Shop,
        name=name,
        logo=_build_logo_file(f"{name}_logo.jpg"),
        type=shop_type,
    )


@pytest.mark.django_db
class TestMigration0023FixSwappedBrandModel:
    """Suite de pruebas para la migración correctiva de Brand/Model invertidos."""

    def test_fixes_swapped_brand_model_for_type_t_shops(self):
        """Verifica que la migración corrige Product que apuntan a Model/Brand invertidos."""
        # Setup: Crear tienda de tipo "T" (Tienda)
        shop = _get_or_create_shop("Tienda Test1", shop_type=Shop.TYPE_CHOICES.TECH)

        # Escenario de inversión: Model.name = Brand.name (indicador de error)
        # Correcto: Model "Teléfonos" con Brand "Samsung"
        samsung_brand = baker.make(Brand, name="Samsung1")
        teléfonos_model = baker.make(Model, name="Teléfonos1", brand=samsung_brand)

        # Invertido: Model "Samsung" (toma nombre del Brand) con Brand "Teléfonos"
        teléfonos_brand = baker.make(Brand, name="Teléfonos1")
        samsung_model = baker.make(Model, name="Samsung1", brand=teléfonos_brand)

        # Crear producto que apunta al Model invertido
        product = baker.make(Product, name="Galaxy A17", model=samsung_model)
        baker.make(
            ShopProducts, shop=shop, product=product, cost_price=0.5, sell_price=1.0
        )

        # Ejecutar migración
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)

        # Verificar: Producto debe apuntar al Model correcto
        product.refresh_from_db()
        assert product.model.id == teléfonos_model.id
        assert product.model.brand.id == samsung_brand.id

    def test_deletes_incorrect_brands_after_reassignment(self):
        """Verifica que la migración elimina Brand erróneos cuando quedan huérfanos."""
        shop = _get_or_create_shop("Tienda Test2", shop_type=Shop.TYPE_CHOICES.TECH)

        # Correcto: Model "Teléfonos" con Brand "Xiaomi"
        xiaomi_brand = baker.make(Brand, name="Xiaomi2")
        teléfonos_model = baker.make(Model, name="Teléfonos2", brand=xiaomi_brand)

        # Invertido: Model "Xiaomi" con Brand "Teléfonos" (será eliminado)
        teléfonos_brand = baker.make(Brand, name="Teléfonos2")
        xiaomi_model = baker.make(Model, name="Xiaomi2", brand=teléfonos_brand)

        # Crear producto que apunta al Model invertido
        product = baker.make(Product, name="Redmi Note 15", model=xiaomi_model)
        baker.make(
            ShopProducts, shop=shop, product=product, cost_price=0.5, sell_price=1.0
        )

        # Guardar ID del Brand incorrecto para verificar eliminación
        incorrect_brand_id = teléfonos_brand.id

        # Ejecutar migración
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)

        # Verificar: Producto apunta al Model correcto con su Brand correcto
        product.refresh_from_db()
        assert product.model.id == teléfonos_model.id
        assert product.model.brand.id == xiaomi_brand.id
        # Verificar: Brand incorrecto debe estar eliminado (estaba huérfano)
        assert not Brand.objects.filter(id=incorrect_brand_id).exists()
        # Verificar: Brand correcto debe existir
        assert Brand.objects.filter(id=xiaomi_brand.id).exists()

    def test_only_affects_type_t_shops(self):
        """Verifica que solo productos en tiendas tipo 'T' son afectados."""
        # Crear tienda de tipo "T"
        shop_t = _get_or_create_shop("Tienda T3", shop_type=Shop.TYPE_CHOICES.TECH)

        # Crear tienda de otro tipo (MECANIC, no TECH)
        shop_other = _get_or_create_shop(
            "Tienda Otro3", shop_type=Shop.TYPE_CHOICES.MECANIC
        )

        # Setup: Correcto
        samsung_brand = baker.make(Brand, name="Samsung3")
        teléfonos_model = baker.make(Model, name="Teléfonos3", brand=samsung_brand)

        # Setup: Invertido
        teléfonos_brand = baker.make(Brand, name="Teléfonos3")
        samsung_model = baker.make(Model, name="Samsung3", brand=teléfonos_brand)

        # Crear producto en tienda "T" (será reparado)
        product_t = baker.make(Product, name="Galaxy F07", model=samsung_model)
        baker.make(
            ShopProducts, shop=shop_t, product=product_t, cost_price=0.5, sell_price=1.0
        )

        # Crear producto en tienda "Otro" (no será reparado)
        product_other = baker.make(Product, name="Galaxy F07b", model=samsung_model)
        baker.make(
            ShopProducts,
            shop=shop_other,
            product=product_other,
            cost_price=0.5,
            sell_price=1.0,
        )

        # Ejecutar migración
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)

        # Verificar: Producto en tienda "T" fue reparado
        product_t.refresh_from_db()
        assert product_t.model.id == teléfonos_model.id
        assert product_t.model.brand.id == samsung_brand.id

        # Verificar: Producto en tienda "Otro" NO fue reparado
        product_other.refresh_from_db()
        assert product_other.model.id == samsung_model.id
        assert product_other.model.brand.id == teléfonos_brand.id

    def test_handles_multiple_products_with_same_name(self):
        """Verifica que la migración maneja correctamente productos con el mismo nombre."""
        shop = _get_or_create_shop("Tienda Test4", shop_type=Shop.TYPE_CHOICES.TECH)

        # Setup: Crear Brand y Model correctos
        samsung_brand = baker.make(Brand, name="Samsung4")
        teléfonos_model = baker.make(Model, name="Teléfonos4", brand=samsung_brand)

        # Setup: Crear Brand y Model invertidos
        teléfonos_brand = baker.make(Brand, name="Teléfonos4")
        samsung_model = baker.make(Model, name="Samsung4", brand=teléfonos_brand)

        # Crear múltiples productos con el mismo nombre (case real en BD)
        product1 = baker.make(Product, name="Galaxy A06", model=samsung_model)
        product2 = baker.make(Product, name="Galaxy A06", model=samsung_model)
        baker.make(
            ShopProducts, shop=shop, product=product1, cost_price=0.5, sell_price=1.0
        )
        baker.make(
            ShopProducts, shop=shop, product=product2, cost_price=0.5, sell_price=1.0
        )

        # Ejecutar migración
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)

        # Verificar: Ambos productos fueron reparados
        product1.refresh_from_db()
        product2.refresh_from_db()
        assert product1.model.id == teléfonos_model.id
        assert product1.model.brand.id == samsung_brand.id
        assert product2.model.id == teléfonos_model.id
        assert product2.model.brand.id == samsung_brand.id

    def test_preserves_valid_brand_model_relationships(self):
        """Verifica que la migración no toca relaciones Brand/Model correctas."""
        shop = _get_or_create_shop("Tienda Test5", shop_type=Shop.TYPE_CHOICES.TECH)

        # Crear Brand y Model CORRECTOS (relación válida)
        apple_brand = baker.make(Brand, name="Apple5")
        iphone_model = baker.make(Model, name="iPhone5", brand=apple_brand)
        product_valid = baker.make(Product, name="iPhone 15", model=iphone_model)
        baker.make(
            ShopProducts,
            shop=shop,
            product=product_valid,
            cost_price=0.5,
            sell_price=1.0,
        )

        # Crear Brand y Model INVERTIDOS (para crear contexto de corrección)
        teléfonos_brand = baker.make(Brand, name="Teléfonos5_inv")
        samsung_model = baker.make(Model, name="Samsung5_inv", brand=teléfonos_brand)
        product_invalid = baker.make(Product, name="Galaxy S24", model=samsung_model)
        baker.make(
            ShopProducts,
            shop=shop,
            product=product_invalid,
            cost_price=0.5,
            sell_price=1.0,
        )

        # Ejecutar migración
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)

        # Verificar: Producto válido no fue alterado
        product_valid.refresh_from_db()
        assert product_valid.model.id == iphone_model.id
        assert product_valid.model.brand.id == apple_brand.id

    def test_does_not_delete_brand_still_referenced_by_other_models(self):
        """Verifica que no se elimina un Brand si aún tiene otros Model asociados."""
        shop = _get_or_create_shop("Tienda Test6", shop_type=Shop.TYPE_CHOICES.TECH)

        # Brand "Samsung6" tiene DOS models: "Teléfonos6" (correcto) y "Tablets6".
        # Aunque "Teléfonos6" sea el correcto para la reparación,
        # "Samsung6" no debe borrarse porque aún tiene "Tablets6".
        samsung_brand = baker.make(Brand, name="Samsung6")
        teléfonos_model = baker.make(Model, name="Teléfonos6", brand=samsung_brand)

        # Par invertido: Brand "Teléfonos6" con Model "Samsung6"
        teléfonos_brand = baker.make(Brand, name="Teléfonos6")
        samsung_model = baker.make(Model, name="Samsung6", brand=teléfonos_brand)

        product = baker.make(Product, name="Galaxy A06c", model=samsung_model)
        baker.make(
            ShopProducts, shop=shop, product=product, cost_price=0.5, sell_price=1.0
        )

        # Ejecutar migración
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)

        # Verificar: Producto fue reparado al Model/Brand correcto
        product.refresh_from_db()
        assert product.model.id == teléfonos_model.id
        assert product.model.brand.id == samsung_brand.id
        # Verificar: Brand "Samsung6" sigue existiendo porque aún tiene "Tablets6"
        assert Brand.objects.filter(id=samsung_brand.id).exists()
        assert Model.objects.filter(brand_id=samsung_brand.id).count() == 2

    def test_idempotent_execution(self):
        """Verifica que ejecutar la migración dos veces no causa problemas."""
        shop = _get_or_create_shop("Tienda Test7", shop_type=Shop.TYPE_CHOICES.TECH)

        # Setup
        samsung_brand = baker.make(Brand, name="Samsung7")
        teléfonos_model = baker.make(Model, name="Teléfonos7", brand=samsung_brand)
        teléfonos_brand = baker.make(Brand, name="Teléfonos7")
        samsung_model = baker.make(Model, name="Samsung7", brand=teléfonos_brand)
        product = baker.make(Product, name="Galaxy A16", model=samsung_model)
        baker.make(
            ShopProducts, shop=shop, product=product, cost_price=0.5, sell_price=1.0
        )

        # Primera ejecución
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)
        product.refresh_from_db()
        model_id_after_first = product.model.id

        # Segunda ejecución (idempotencia)
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)
        product.refresh_from_db()
        model_id_after_second = product.model.id

        # Verificar: Model y Brand deben ser los correctos en ambas ejecuciones
        assert model_id_after_first == model_id_after_second == teléfonos_model.id
        assert product.model.brand.id == samsung_brand.id

    def test_handles_missing_correct_model_gracefully(self):
        """Verifica que la migración maneja casos donde no existe el Model correcto."""
        shop = _get_or_create_shop("Tienda Test8", shop_type=Shop.TYPE_CHOICES.TECH)

        # Setup: Solo crear Brand y Model INVERTIDOS, sin los correctos
        teléfonos_brand = baker.make(Brand, name="Teléfonos8_inv")
        samsung_model = baker.make(Model, name="Samsung8_inv", brand=teléfonos_brand)
        product = baker.make(Product, name="Galaxy A05", model=samsung_model)
        baker.make(
            ShopProducts, shop=shop, product=product, cost_price=0.5, sell_price=1.0
        )

        # Ejecutar migración (no debería fallar aunque no exista el Model correcto)
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)

        # Verificar: Producto sigue apuntando al mismo Model (no hay Model correcto)
        product.refresh_from_db()
        assert product.model.id == samsung_model.id

    def test_comprehensive_scenario_multiple_errors(self):
        """
        Prueba integral: múltiples productos con Brand/Model invertidos,
        algunos correctos, diferentes tipos de tienda.
        """
        # Tienda tipo "T" (será procesada)
        shop_t = _get_or_create_shop(
            "Almacén Central9", shop_type=Shop.TYPE_CHOICES.TECH
        )
        # Tienda tipo Mecánica (NO será procesada, tipo != "T")
        shop_distributor = _get_or_create_shop(
            "Distribuidor X9", shop_type=Shop.TYPE_CHOICES.MECANIC
        )

        # Scenario 1: Brand/Model correcto (no debe ser alterado)
        samsung_brand = baker.make(Brand, name="Samsung9")
        teléfonos_model = baker.make(Model, name="Teléfonos9", brand=samsung_brand)
        p_correct = baker.make(Product, name="Galaxy A17", model=teléfonos_model)
        baker.make(
            ShopProducts, shop=shop_t, product=p_correct, cost_price=0.5, sell_price=1.0
        )

        # Scenario 2: Brand/Model invertido en tienda "T" (debe repararse)
        teléfonos_brand = baker.make(Brand, name="Teléfonos9")
        samsung_model = baker.make(Model, name="Samsung9", brand=teléfonos_brand)
        p_swapped_t = baker.make(Product, name="Galaxy F07", model=samsung_model)
        baker.make(
            ShopProducts,
            shop=shop_t,
            product=p_swapped_t,
            cost_price=0.5,
            sell_price=1.0,
        )

        # Scenario 3: Brand/Model invertido en tienda Mecánica (NO debe repararse, tipo != "T")
        xiaomi_brand = baker.make(Brand, name="Xiaomi9")
        redmi_model = baker.make(Model, name="Redmi9", brand=xiaomi_brand)
        p_swapped_dist = baker.make(Product, name="Redmi Note 15", model=redmi_model)
        baker.make(
            ShopProducts,
            shop=shop_distributor,
            product=p_swapped_dist,
            cost_price=0.5,
            sell_price=1.0,
        )

        # Ejecutar migración
        MIGRATION_MODULE.fix_swapped_brand_model_data(django_apps, None)

        # Verificaciones
        p_correct.refresh_from_db()
        p_swapped_t.refresh_from_db()
        p_swapped_dist.refresh_from_db()

        # Scenario 1: No debe cambiar
        assert p_correct.model.id == teléfonos_model.id
        assert p_correct.model.brand.id == samsung_brand.id

        # Scenario 2: Debe ser reparado al Model/Brand correcto
        assert p_swapped_t.model.id == teléfonos_model.id
        assert p_swapped_t.model.brand.id == samsung_brand.id

        # Scenario 3: No debe cambiar (diferente tipo de tienda)
        assert p_swapped_dist.model.id == redmi_model.id
        assert p_swapped_dist.model.brand.id == xiaomi_brand.id

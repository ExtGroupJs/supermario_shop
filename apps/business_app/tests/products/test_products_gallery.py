import tempfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from model_bakery import baker
from PIL import Image

from apps.business_app.models.gallery import Gallery
from apps.business_app.models.product import Product
from apps.common.baseclass_for_testing import BaseTestClass
from apps.users_app.models.groups import Groups


def imagen_valida(nombre="test.png"):
    from io import BytesIO

    buffer = BytesIO()
    Image.new("RGB", (1, 1)).save(buffer, format="PNG")
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type="image/png")


@pytest.mark.django_db
class TestProductsGallery(BaseTestClass):
    fixtures = ["auth.group.json"]

    def setUp(self):
        super().setUp()
        self.user.groups.add(Groups.SUPER_ADMIN.value)
        self.client.force_authenticate(self.user)

    def test_product_returns_gallery_images(self):
        """
        El producto expone la galería como listado de imágenes
        """
        product = baker.make(Product)
        baker.make(Gallery, product=product, image="gallery_1.png")
        baker.make(Gallery, product=product, image="gallery_2.png")

        response = self.client.get(
            reverse("products-detail", kwargs={"pk": product.id})
        )

        print("\n--- DEBUG RETRIEVE ---")
        print("Response Data Keys:", response.data.keys())
        print("Response Data:", response.data)
        print("---------------------\n")

        assert response.status_code == 200
        assert len(response.data["gallery"]) == 2
        assert all(isinstance(image, str) for image in response.data["gallery"])

    def test_can_add_multiple_images_to_a_product(self):
        """
        Se pueden asociar varias imágenes a un mismo producto
        """
        product = baker.make(Product)
        url = reverse("galleries-list")

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                for nombre in ("gallery_1.png", "gallery_2.png"):
                    response = self.client.post(
                        url,
                        {"product": product.id, "image": imagen_valida(nombre)},
                        format="multipart",
                    )
                    assert response.status_code == 201

        assert Gallery.objects.filter(product=product).count() == 2

    def test_gallery_is_removed_when_product_is_deleted(self):
        """
        Al eliminar el producto se eliminan sus imágenes de galería
        """
        product = baker.make(Product)
        baker.make(Gallery, product=product, image="gallery_1.png")

        product.delete()

        assert Gallery.objects.filter(product=product).count() == 0

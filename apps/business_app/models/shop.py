from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError


class Shop(models.Model):
    WHOLESALE_SHOP_NAME = "Tienda al por mayor"
    TYPE_MECHANIC = "mecanica"
    TYPE_TECHNOLOGY = "tecnologia"
    TYPE_FOOD = "alimentos"
    TYPE_OTHER = "otros"
    TYPE_CHOICES = (
        (TYPE_MECHANIC, "Mecanica"),
        (TYPE_TECHNOLOGY, "Tecnologia"),
        (TYPE_FOOD, "Alimentos"),
        (TYPE_OTHER, "Otros"),
    )

    name = models.CharField(verbose_name="Nombre", unique=True, max_length=200)
    catalog_url = models.SlugField(
        verbose_name="URL catálogo",
        unique=True,
        max_length=255,
        null=True,
        blank=True,
    )
    logo = models.ImageField(verbose_name="logo")
    extra_info = models.TextField(
        verbose_name="Información Extra", null=True, blank=True
    )
    type = models.CharField(
        verbose_name="Tipo",
        max_length=20,
        choices=TYPE_CHOICES,
        null=True,
        blank=True,
        default=None,
    )
    products = models.ManyToManyField(
        to="business_app.Product", through="business_app.ShopProducts"
    )
    enabled = models.BooleanField(verbose_name="Habilitado", default=True)
    principal = models.BooleanField(verbose_name="Principal", default=False)

    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"
        constraints = [
            models.UniqueConstraint(
                fields=["principal"],
                condition=Q(principal=True),
                name="unique_principal_shop",
            )
        ]

    def clean(self):
        super().clean()
        if self.principal:
            another_principal_exists = (
                Shop.objects.filter(principal=True).exclude(pk=self.pk).exists()
            )
            if another_principal_exists:
                raise ValidationError(
                    {"principal": "Solo puede existir una tienda principal."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

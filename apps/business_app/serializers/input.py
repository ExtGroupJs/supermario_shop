from rest_framework import serializers

from apps.business_app.models.input import Input


class InputSerializer(serializers.ModelSerializer):
    # product_name = serializers.CharField(read_only=True)
    created_timestamp = serializers.SerializerMethodField()
    for_date = serializers.SerializerMethodField()
    shop_product_name = serializers.StringRelatedField(
        source="shop_product", read_only=True
    )
    author_name=serializers.StringRelatedField(source="author", read_only=True)

    class Meta:
        model = Input
        fields = (
            "id",
            "shop_product",
            "shop_product_name",
            "quantity",
            "created_timestamp",
            "for_date",
            "author",
            "author_name",
        )
        read_only_fields = ("id",)

    def get_created_timestamp(self, object):
        return object.created_timestamp.strftime("%d-%h-%Y a las %I:%M %p")

    def get_for_date(self, object):
        return object.input_group.for_date.strftime("%d-%h-%Y")

    def validate_quantity(self, value):
        if not value:
            raise serializers.ValidationError(
                "La entrada debe tener al menos un elemento"
            )
        return value

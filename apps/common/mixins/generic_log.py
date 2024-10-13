from argparse import Action
from django.db import models
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.common.models.generic_log import GenericLog
from apps.users_app.models.system_user import SystemUser


class GenericLogMixin:
    def save(self, *args, **kwargs):
        updated_object_dict = model_to_dict(self)
        action = GenericLog.ACTION.UPDATED
        details = {}
        if self.pk is not None:
            original_object = self.__class__.objects.get(pk=self.pk)
            original_object_dict = model_to_dict(original_object)
            for field, new_value in updated_object_dict.items():
                original_value = original_object_dict.get(field)
                if original_value != new_value:
                    details[field] = {
                        "old_value": str(getattr(original_object, field)),
                        "new_value": str(getattr(self, field)),
                    }
        else:
            action = GenericLog.ACTION.CREATED
            for field, new_value in updated_object_dict.items():
                if new_value:
                    details[field] = str(getattr(self, field))
        super().save(*args, **kwargs)
        if details:
            GenericLog.objects.create(
                performed_action=action,
                content_type=ContentType.objects.get_for_model(self.__class__),
                object_id=self.pk,
                details=str(details),
            )

    def delete(self, *args, **kwargs):
        GenericLog.objects.create(
            performed_action=GenericLog.ACTION.DELETED,
            content_type=ContentType.objects.get_for_model(self.__class__),
            object_id=self.pk,
        )
        super().delete(*args, **kwargs)

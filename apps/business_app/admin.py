from django.contrib import admin
from solo.admin import SingletonModelAdmin
import logging


# from apps.business_app.models import (
    # AllowedExtensions,
    # SiteConfiguration,
    # UploadedFiles,
    # AlleleNode,
    # Marker,
    # Event,
    # Layer,
    # WorkingCopyOfOriginalFile,
# )
# from apps.business_app.models.initial_file_data import InitialFileData
# from apps.business_app.models.pdb_files import PdbFiles

# logger = logging.getLogger(__name__)

# # Register your models here.

# admin.site.register(SiteConfiguration, SingletonModelAdmin)
# admin.site.register(Event)
# admin.site.register(Marker)
# admin.site.register(Layer)


# @admin.register(AlleleNode)
# class AlleleNodeAdmin(admin.ModelAdmin):
    # empty_value_display = "-empty-"
    # list_display = [
        # "id",
        # "number",
        # "unique_number",
        # "element",
        # "custom_element_name",
        # "symbol",
        # "rs",
        # "uploaded_file",
    # ]
    # fields = [
        # "number",
        # "element",
        # "custom_element_name",
        # "symbol",
        # "rs",
        # "uploaded_file",
    # ]


# @admin.register(AllowedExtensions)
# class AllowedExtensionsAdmin(admin.ModelAdmin):
    # empty_value_display = "-empty-"
    # list_display = [
        # "id",
        # "extension",
        # "typical_app_name",
    # ]
    # fields = [
        # "extension",
        # "typical_app_name",
    # ]


# @admin.register(UploadedFiles)
# class UploadedFilesAdmin(admin.ModelAdmin):
    # empty_value_display = "-empty-"
    # list_display = [
        # "id",
        # "custom_name",
        # "description",
        # "original_file",
        # "system_user",
        # "google_sheet_id",
    # ]
    # fields = [
        # "custom_name",
        # "description",
        # "original_file",
        # "system_user",
        # "google_sheet_id",
    # ]

    # def save_model(self, request, obj, form, change):
        # try:
            # obj.save()
        # except Exception as e:
            # logger.error(f"{str(e)}")
            # # Display the exception in the admin interface
            # self.message_user(request, f"{str(e)}", level="error")


# @admin.register(PdbFiles)
# class PdbFilesAdmin(admin.ModelAdmin):
    # empty_value_display = "-empty-"
    # list_display = [
        # "id",
        # "custom_name",
        # "description",
        # "original_file",
        # "file",
    # ]
    # fields = [
        # "custom_name",
        # "description",
    # ]


# @admin.register(WorkingCopyOfOriginalFile)
# class WorkingCopyOfOriginalFileAdmin(admin.ModelAdmin):
    # empty_value_display = "-empty-"
    # list_display = [
        # "id",
        # "system_user",
        # "uploaded_file",
        # "pdb_file_copy",
    # ]
    # fields = [
        # "id",
        # "uploaded_file",
    # ]


# @admin.register(InitialFileData)
# class InitialFileDataAdmin(admin.ModelAdmin):
    # empty_value_display = "-empty-"
    # list_display = [
        # "id",
        # "row_index",
        # "allele",
        # "marker",
        # "original_value",
        # "min_value",
        # "max_value",
        # "uploaded_file_id",
    # ]
    # fields = [
        # "allele",
        # "marker",
        # "min_value",
        # "max_value",
        # "uploaded_file",
    # ]

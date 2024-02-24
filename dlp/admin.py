from django.contrib import admin

from dlp.models import DLPPattern


@admin.register(DLPPattern)
class DLPPatternAdmin(admin.ModelAdmin):
    pass

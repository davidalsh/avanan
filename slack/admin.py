from django.contrib import admin

from slack.models import FlaggedMessage


@admin.register(FlaggedMessage)
class FlaggedMessageAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields

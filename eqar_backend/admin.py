import nested_admin
from django.contrib import admin
from django.contrib.admin import AdminSite, StackedInline, TabularInline
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.db import models
from django.forms import TextInput, Textarea, Select


class DEQARAutocompleteJsonView(AutocompleteJsonView):
    """
    Lets a ModelAdmin define autocomplete_label(obj) to label its objects differently from str(obj).
    """
    def serialize_result(self, obj, to_field_name):
        result = super().serialize_result(obj, to_field_name)
        if hasattr(self.model_admin, 'autocomplete_label'):
            result['text'] = self.model_admin.autocomplete_label(obj)
        return result


class DEQARAdminSite(AdminSite):
    site_header = 'DEQAR Administration'
    site_title = 'DEQAR Administration'
    index_title = 'View/Edit entries in'

    def autocomplete_view(self, request):
        return DEQARAutocompleteJsonView.as_view(admin_site=self)(request)


class DEQARModelAdmin(admin.ModelAdmin):
    pass


class DEQARStackedInline(StackedInline):
    pass


class DEQARTabularInline(TabularInline):
    pass


class DEQARNestedModelAdmin(nested_admin.NestedModelAdmin):
    pass


class DEQARNestedStackedInline(nested_admin.NestedStackedInline):
    pass


class DEQARNestedTabularInline(nested_admin.NestedTabularInline):
    pass

admin_site = DEQARAdminSite(name='deqar_admin')

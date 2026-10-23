import nested_admin
from django.contrib import admin
from django.contrib.admin import AdminSite, StackedInline, TabularInline
from django.db import models
from django.forms import TextInput, Textarea, Select


class DEQARAdminSite(AdminSite):
    site_header = 'DEQAR Administration'
    site_title = 'DEQAR Administration'
    index_title = 'View/Edit entries in'


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

from django.contrib import admin
from django.contrib.admin import AdminSite, StackedInline, TabularInline
from django.db import models
from django.forms import TextInput, Textarea, Select


class DEQARAdminSite(AdminSite):
    site_header = 'DEQAR Administration'
    site_title = 'DEQAR Administration'
    index_title = 'View/Edit entries in'


class DEQARModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'span8'})},
        models.TextField: {'widget': Textarea(attrs={'class': 'span8', 'rows': 4})},
        models.URLField: {'widget': TextInput(attrs={'class': 'span8'})},
        models.ForeignKey: {'widget': Select(attrs={'class': 'span8'})},
    }


class DEQARStackedInline(StackedInline):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'span8'})},
        models.TextField: {'widget': Textarea(attrs={'class': 'span8', 'rows': 4})},
        models.URLField: {'widget': TextInput(attrs={'class': 'span8'})},
        models.ForeignKey: {'widget': Select(attrs={'class': 'span8'})},
    }


class DEQARTabularInline(TabularInline):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'class': 'span8'})},
        models.TextField: {'widget': Textarea(attrs={'class': 'span8', 'rows': 4})},
        models.URLField: {'widget': TextInput(attrs={'class': 'span8'})},
        models.ForeignKey: {'widget': Select(attrs={'class': 'span8'})},
    }

admin_site = DEQARAdminSite(name='deqar_admin')

from django.contrib import admin
from django.contrib.auth.models import User
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import Token

from accounts.models import DEQARProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from eqar_backend.admin import admin_site


class DEQARProfileInline(admin.StackedInline):
    model = DEQARProfile
    can_delete = False
    verbose_name_plural = 'DEQAR Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (DEQARProfileInline, )


# Re-register UserAdmin
admin_site.register(User, UserAdmin)
admin_site.register(Token, TokenAdmin)

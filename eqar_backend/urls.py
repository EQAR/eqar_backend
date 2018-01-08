from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from eqar_backend.admin import admin_site

urlpatterns = [
    url(r'^webapi/v1/', include('webapi.urls', namespace='webapi-v1')),

    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', admin_site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


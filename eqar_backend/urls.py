import debug_toolbar
from django.urls import re_path, include
from django.conf import settings
from django.conf.urls.static import static
from eqar_backend.admin import admin_site

urlpatterns = [
    re_path(r'^webapi/v2/', include('webapi.v2.urls', namespace='webapi-v2')),

    re_path(r'^submissionapi/v1/', include('submissionapi.v1.urls', namespace='submissionapi-v1')),
    re_path(r'^submissionapi/v2/', include('submissionapi.v2.urls', namespace='submissionapi-v2')),

    re_path(r'^adminapi/v1/', include('adminapi.urls', namespace='adminapi-v1')),
    re_path(r'^connectapi/v1/', include('connectapi.urls', namespace='connectapi-v1')),

    re_path(r'^accounts/', include('accounts.urls', namespace='accounts')),
    re_path(r'^admin/', admin_site.urls),
    re_path(r'^auth/', include('djoser.urls')),

    re_path(r'^__debug__/', include(debug_toolbar.urls))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


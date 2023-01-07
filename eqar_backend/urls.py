import debug_toolbar
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from eqar_backend.admin import admin_site

urlpatterns = [
    url(r'^webapi/v1/', include('webapi.urls', namespace='webapi-v1')),
    url(r'^webapi/v2/', include('webapi.urls_v2', namespace='webapi-v2')),

    url(r'^submissionapi/v1/', include('submissionapi.urls', namespace='submissionapi-v1')),
    url(r'^adminapi/v1/', include('adminapi.urls', namespace='adminapi-v1')),
    url(r'^connectapi/v1/', include('connectapi.urls', namespace='connectapi-v1')),

    url(r'^api/v3/reports/', include('reports.routes.v3.urls', namespace='reports-v3')),

    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^admin/', admin_site.urls),
    url(r'^auth/', include('djoser.urls')),

    url(r'^__debug__/', include(debug_toolbar.urls))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


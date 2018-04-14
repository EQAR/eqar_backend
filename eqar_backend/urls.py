import debug_toolbar
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from eqar_backend.admin import admin_site

urlpatterns = [
    url(r'^webapi/v1/', include('webapi.urls', namespace='webapi-v1')),
    url(r'^submissionapi/v1/', include('submissionapi.urls', namespace='submissionapi-v1')),
    url(r'^adminapi/v1/', include('adminapi.urls', namespace='adminapi-v1')),

    url(r'^csvtest/', include('csvtest.urls', namespace='csvtest')),

    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^admin/', admin_site.urls),
    url(r'^auth/', include('djoser.urls')),

    url(r'^login/', auth_views.login, name='login'),
    url(r'^logout/', auth_views.logout, name='logout'),

    url(r'^__debug__/', include(debug_toolbar.urls))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


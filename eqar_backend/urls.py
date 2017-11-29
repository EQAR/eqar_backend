from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^api/', include('discovery_api.urls', namespace='discovery_api')),
    url(r'^admin/', admin.site.urls),
]

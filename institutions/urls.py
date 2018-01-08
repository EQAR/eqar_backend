from django.conf.urls import url

from institutions.views import SyncETERView

urlpatterns = [
    url(r'^sync-eter/$', SyncETERView.as_view(), name='sync-eter'),
]
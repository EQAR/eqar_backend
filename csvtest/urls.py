from django.conf.urls import url
from csvtest import views

urlpatterns = [
    url(r'^upload/$', views.upload_csv, name='upload_csv'),
]
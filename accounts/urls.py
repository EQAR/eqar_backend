from django.conf.urls import url
from accounts.views import GetAuthToken

urlpatterns = [
    url(r'^get_token/', GetAuthToken.as_view())
]
from django.conf.urls import url
from accounts.views import GetAuthToken, ChangeEmailView, GetNewAuthToken

urlpatterns = [
    url(r'^get_token/', GetAuthToken.as_view()),
    url(r'^change_email/', ChangeEmailView.as_view()),
    url(r'^get_new_token/', GetNewAuthToken.as_view())
]
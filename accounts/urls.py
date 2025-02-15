from django.urls import re_path

from accounts.views import GetAuthToken, ChangeEmailView, GetNewAuthToken

app_name = 'accounts'

urlpatterns = [
    re_path(r'^get_token/', GetAuthToken.as_view()),
    re_path(r'^change_email/', ChangeEmailView.as_view()),
    re_path(r'^get_new_token/', GetNewAuthToken.as_view())
]
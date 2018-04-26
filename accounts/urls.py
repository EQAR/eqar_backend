from django.conf.urls import url
from accounts.views import GetAuthToken, ChangeEmailView

urlpatterns = [
    url(r'^get_token/', GetAuthToken.as_view()),
    url(r'^change_email/', ChangeEmailView.as_view())
]
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

# Create your views here.
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.status import HTTP_401_UNAUTHORIZED


class GetAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'state': 'success',
                'token': token.key,
                'account': user.username
            })
        else:
            return Response({
                'state': 'error',
                'errorMessage': "Unable to log in with provided credentials."
            }, status=HTTP_401_UNAUTHORIZED)
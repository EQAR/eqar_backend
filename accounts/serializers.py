from django.contrib.auth.models import User
from rest_framework import serializers


class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    re_new_email = serializers.EmailField()

    def validate(self, data):
        new_email = data.get('new_email', None)
        re_new_email = data.get('re_new_email', None)

        if new_email != re_new_email:
            raise serializers.ValidationError("Please provide identical e-mail addresses.")

        return data


class CurrentUserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    def get_is_admin(self, obj):
        return obj.is_superuser

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_admin')

from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        return user

    class Meta:
        model = UserModel
        fields = ('password', 'username', 'first_name', 'last_name',)

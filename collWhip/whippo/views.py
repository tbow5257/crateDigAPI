from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

class CreateUserView(CreateModelMixin, GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

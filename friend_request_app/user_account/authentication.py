""" Import Django libraries """
import re
# from django.conf import settings
from django.db.models import Q 
from django.contrib.auth.models import User
from django.db.models.functions import Concat
from django.db.models import Value
import pandas as pd

""" Import rest framework libraries """
import datetime
# from accuknox_assesment import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer

# class CustomUsernameField(serializers.CharField):
#     def validate(self, value):
#         try:
#             user = User.objects.get(Q(username=value) | Q(email=value))
#             return value
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Invalid username or email")

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


    def validate_username(self, value):
        try:
            user = User.objects.get(Q(username=value) | Q(email=value))
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or email")

    def validate(self, attrs):
        try:
            # Try to get user by username or email
            user = User.objects.filter(Q(username=attrs['username']) | Q(email=attrs['username'])).first()
            if not user:
                raise serializers.ValidationError("Invalid username or email")

            # Validate password
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError("Invalid password")
            # data=[]
            refresh = self.get_token(user)

            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'access_token_lifetime': int(refresh.access_token.lifetime.total_seconds()),
                'access_token_expiry': str(datetime.datetime.now() + refresh.access_token.lifetime),
                'refresh_expires_in': int(refresh.lifetime.total_seconds()),
                'refresh_token_expiry': str(datetime.datetime.now() + refresh.lifetime)
            }
            return data
        except Exception as e:
            raise serializers.ValidationError("Invalid username or password")
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


 
class CustomRefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            # Call the parent validate method to continue the token validation process
            data = super().validate(attrs)
            refresh = RefreshToken(attrs['refresh'])
            response_data = {
                "access": data['access'],
                'access_token_lifetime' :int(refresh.access_token.lifetime.total_seconds()),
                'access_token_expiry': str(datetime.datetime.now() + refresh.access_token.lifetime),
                "refresh": attrs['refresh'],
                'refresh_expires_in' : int(refresh.lifetime.total_seconds()),
                'refresh_token_expiry' : str(datetime.datetime.now() + refresh.lifetime),
            }
            return response_data
        except Exception as e:
            raise serializers.ValidationError("Invalid refresh token")

class CustomRefreshTokenPairView(TokenRefreshView):
    serializer_class = CustomRefreshTokenSerializer
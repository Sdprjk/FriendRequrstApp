import json
import os
import pandas as pd

from tokenize import TokenError
# from django.conf import settings
from django.db import models
from django.db.models import Q, fields
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
import random
import string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
import datetime

from user_account.models import FriendRequest


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['password'] = user.password
        # token['client_id'] = settings.AUTHENTICATION_PROVIDERS['my_provider']['CLIENT_ID']
        # token['client_secret'] = settings.AUTHENTICATION_PROVIDERS['my_provider']['CLIENT_SECRET']

        return token
class UserViewSerializer(serializers.ModelSerializer):

    class Meta():
        model=User
        fields=("id","username","first_name", "last_name","email","is_active")

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields=("id","username","first_name","last_name","password","email","is_staff","is_active")

class FriendRequestSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender_id.username', default='', read_only=True)

    class Meta:
        model = FriendRequest
        fields=("fr_id","receiver_id","sender_id","sender_name","is_rejected","is_accepted","extras","is_deleted","is_active","created_by","created_at","updated_by","updated_at")
    
    
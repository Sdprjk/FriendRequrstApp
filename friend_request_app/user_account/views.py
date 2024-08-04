""" Import Django libraries """
from datetime import timedelta, timezone
import datetime
import logging
import re
from django.conf import settings
from django.db.models import Q 
from django.contrib.auth.models import User
import pandas as pd

from user_account import controller
from user_account.models import FriendRequest
from user_account.serializer import FriendRequestSerializer, UserSerializer, UserViewSerializer



""" Import rest framework libraries """
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


""" Import Swagger """
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import requests


# ca_bundle_path = '/path/to/ca/bundle.crt'
# requests.get('https://pypi.python.org/pypi/pandas/json', verify=ca_bundle_path)
# response = requests.get('https://pypi.python.org/pypi/pandas/json', verify=settings.REQUESTS_CA_BUNDLE)


# Get an instance of a logging
log = logging.getLogger(__name__)

# Create your views here.

class SignupViewSet(ViewSet):
    mail_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    pass_reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING, description="username"
                ),
                "first_name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="first_name"
                ),
                "last_name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="last_name"
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="email"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="password"
                ),
            },
        ),
    )
    def signup(self,request):
        '''create new user '''
        log.info("Signup create API")
        log.info(request.data)
        superadmin=False
        admin=False
        try:
            if re.fullmatch(self.mail_regex, request.data['email']):
                log.info("valid email")
                created_data = controller.UserController.createUserDetails(self,request) # create user
                if "error" not in created_data:
                    user_data = UserSerializer(data=created_data,partial=True)
                    if user_data.is_valid():
                        U_data = user_data.save()
                        log.info("user created",user_data.data)
                        
                        user_data = {"id":U_data.id,"username":U_data.username,"first_name":U_data.first_name,"last_name":U_data.last_name,"email":U_data.email,"is_active":U_data.is_active,"is_superadmin":superadmin,"is_admin":admin}
                        return Response({"error": False, "message": 'User created Successfully', "data":user_data,"status": 200}, status=status.HTTP_200_OK) 
                    else:
                        return Response({"error": True, "message": user_data.errors, "status": 400}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": True, "message": created_data["message"], "status": 400}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": True, "message": 'failed to add user valid email required', "status": 400}, status=status.HTTP_400_BAD_REQUEST)
        except Exception  as ex:
            log.error(ex)
            return Response({"error": True, "message": f"we would like to inform you {ex}", "status": 400}, status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(ViewSet):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    mail_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    pass_reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "limit": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Limit"
                ),
                "offset": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Offset"
                ),
                "search_content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Search Content"
                )
            },
        ),
    ) 
    def list(self, request):
        """Return all connection, ordered by recently created
        """
        log.info("UserViewSet list API")
        log.info(request.data)
        try:
            # Application success content
            response_content = {"error":False, "message":"success", "data": "", "status":200}
            condition = Q()
            total_count = 0
            limit = 10
            offset = 0
            if 'offset' in request.data and request.data['offset']:
                offset = request.data['offset']
            if 'limit' in request.data and request.data['limit']:
                limit = request.data['limit']
            if "search_content" in request.data and request.data['search_content'] :
                or_condition = Q(username__icontains=request.data['search_content']) | Q(first_name__icontains=request.data['search_content']) | Q(email__icontains=request.data['search_content']) | Q(last_name__icontains=request.data['search_content']) 
                condition &= or_condition    
            
            total_count = User.objects.filter(condition).count()
            query_set = User.objects.filter(condition).order_by('-id')[int(offset):int(offset) + int(limit)]
            serializer = UserViewSerializer(query_set, many= True)
            response_content['count'] = total_count

            if serializer.data:
                response_content['data'] =serializer.data
            else:
                response_content['data'] = []
            return Response(response_content, status= status.HTTP_200_OK)
        except Exception as e:
            # Application failure content
            log.error("Exception in User list API",e)
            return Response({"error": False, "message": e, "status": 400}, status= status.HTTP_400_BAD_REQUEST)

  

class FriendRequestViewSet(ViewSet):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "receiver_id": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Receiver ID"
                ),
            },
        ),
    )
    def send(self,request):
        try:
            log.info("FriendRequestViewSet send API")
            log.info(request.data)
            if 'receiver_id' in request.data and request.data['receiver_id']:
                if request.data['receiver_id'] != request.user.id: 
                    receiver_id = request.data['receiver_id']
                else:
                    return Response({"error": True, "message": 'receiver_id should not be same', "status": 400}, status= status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": True, "message": 'receiver_id required', "status": 400}, status= status.HTTP_400_BAD_REQUEST)
            
             # Check if the user has already sent more than 3 friend requests in the last minute
            one_minute_ago = datetime.datetime.now() - timedelta(minutes=1)
            condition = Q(sender_id=request.user.id)
            condition &= Q(created_at__gte=one_minute_ago)
            already_sent_count = FriendRequest.objects.filter(condition).count()
            if already_sent_count >= 3:
                return Response({"error": True, "message": 'Too many friend requests sent in the last minute', "status": 400}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has already received a friend request from the receiver
            condition = Q(sender_id=request.user.id)
            condition &= Q(receiver_id=receiver_id)
            condition &= Q(is_active=False)
            condition &= Q(is_accepted=False)
            condition &= Q(is_rejected=False)
            already_send = FriendRequest.objects.filter(condition)
            if already_send:
                return Response({"error": True, "message": 'Already send friend request', "status": 400}, status= status.HTTP_400_BAD_REQUEST)
            
            # Setup friend request to send
            send_data = controller.UserController.sendRequestDetails(self,request)
            if "error" not in send_data:
                    send_friend_request_data = FriendRequestSerializer(data=send_data,partial=True)
                    if send_friend_request_data.is_valid():
                        U_data = send_friend_request_data.save()
                        log.info("user created",send_friend_request_data.data)
            return Response({"error": False, "message": 'Friend Request Send Successfully', "status": 200}, status= status.HTTP_200_OK)
        except Exception as e:
            log.error("Exception in FriendRequest send API",e)
            return Response({"error": False, "message": e, "status": 400}, status= status.HTTP_400_BAD_REQUEST)



    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "sender_id": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Sender ID"
                ),
            },
        ),
    )
    def accept(self,request):
        try:
            log.info("FriendRequestViewSet accept API")
            log.info(request.data)
            if 'sender_id' in request.data and request.data['sender_id']:
                    sender_id = request.data['sender_id']
            else:
                return Response({"error": True, "message": 'sender_id required', "status": 400}, status= status.HTTP_400_BAD_REQUEST)
            
            # Check if the user has already received a friend request from the receiver
            condition = Q(sender_id=sender_id)
            condition &= Q(receiver_id=request.user.id)
            condition &= Q(is_active=True)
            try:
                active_request = FriendRequest.objects.get(condition)
                accept_data = controller.UserController.acceptRequestDetails(self,request)
                if "error" not in accept_data:
                    friend_request_accept_data = FriendRequestSerializer(active_request,data=accept_data,partial=True)
                    if friend_request_accept_data.is_valid():
                        friend_request_accept_data.save()
                        log.info("Friend Request Accepted",friend_request_accept_data.data)
                return Response({"error": False, "message": 'Friend Request Accepted Successfully', "status": 200}, status= status.HTTP_200_OK)
            except FriendRequest.DoesNotExist:
                return Response({"error": True, "message": 'You do not have friend request from that user', "status": 400}, status= status.HTTP_400_BAD_REQUEST)
          
        except Exception as e:
            log.error("Exception in FriendRequest accept API",e)
            return Response({"error": False, "message": e, "status": 400}, status= status.HTTP_400_BAD_REQUEST)





    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "sender_id": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Sender ID"
                ),
            },
        ),
    )
    def reject(self,request):
        try:
            log.info("FriendRequestViewSet reject API")
            log.info(request.data)
            if 'sender_id' in request.data and request.data['sender_id']:
                    sender_id = request.data['sender_id']
            else:
                return Response({"error": True, "message": 'receiver_id required', "status": 400}, status= status.HTTP_400_BAD_REQUEST)
            
            # Check if the user has already received a friend request from the receiver
            condition = Q(sender_id=sender_id)
            condition &= Q(receiver_id=request.user.id)
            condition &= Q(is_active=True)
            try:
                active_request = FriendRequest.objects.get(condition)
                reject_data = controller.UserController.rejectRequestDetails(self,request)
                if "error" not in reject_data:
                    friend_request_reject_data = FriendRequestSerializer(active_request,data=reject_data,partial=True)
                    if friend_request_reject_data.is_valid():
                        friend_request_reject_data.save()
                        log.info("Friend Request Accepted",friend_request_reject_data.data)
                return Response({"error": False, "message": 'Friend Request Rejected', "status": 200}, status= status.HTTP_200_OK)
            except FriendRequest.DoesNotExist:
                return Response({"error": True, "message": 'You do not have friend request from that user', "status": 400}, status= status.HTTP_400_BAD_REQUEST)
          
        except Exception as e:
            log.error("Exception in FriendRequest reject API",e)
            return Response({"error": False, "message": e, "status": 400}, status= status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "limit": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Limit"
                ),
                "offset": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Offset"
                ),
                "search_content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Search Content"
                )
            },
        ),
    ) 
    def friendList(self, request):
        """Return all connection, ordered by recently created
        """
        log.info(" FriendRequestViewSet Friend list API")
        log.info(request.data)
        try:
            # Application success content
            response_content = {"error":False, "message":"success", "data": "", "status":200}
            condition = Q(is_accepted=True)
            condition = Q(receiver_id = request.user.id)
            total_count = 0
            limit = 10
            offset = 0
            if 'offset' in request.data and request.data['offset']:
                offset = request.data['offset']
            if 'limit' in request.data and request.data['limit']:
                limit = request.data['limit']
            if "search_content" in request.data and request.data['search_content'] :
                or_condition = Q(is_accepted__username__icontains=request.data['search_content']) | Q(is_accepted__first_name__icontains=request.data['search_content']) | Q(is_accepted__email__icontains=request.data['search_content']) | Q(is_accepted__last_name__icontains=request.data['search_content']) 
                condition &= or_condition    
            
            total_count = FriendRequest.objects.filter(condition).count()
            query_set = FriendRequest.objects.filter(condition).order_by('-created_at')[int(offset):int(offset) + int(limit)]
            serializer = FriendRequestSerializer(query_set, many= True)
            response_content['count'] = total_count
            friend_list = []
            if serializer.data:
                for friend in serializer.data:
                    friend_list.append(friend['sender_name'])
                response_content["data"] = friend_list
            else:
                response_content['data'] = []
            return Response(response_content, status= status.HTTP_200_OK)
        except Exception as e:
            # Application failure content
            log.error("Exception in Friend list API",e)
            return Response({"error": False, "message": e, "status": 400}, status= status.HTTP_400_BAD_REQUEST)



    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "limit": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Limit"
                ),
                "offset": openapi.Schema(
                    type=openapi.TYPE_NUMBER, description="Offset"
                ),
                "search_content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Search Content"
                )
            },
        ),
    ) 
    def pendingFriendList(self, request):
        """Return all connection, ordered by recently created
        """
        log.info(" FriendRequestViewSet Friend list API")
        log.info(request.data)
        try:
            # Application success content
            response_content = {"error":False, "message":"success", "data": "", "status":200}
            condition = Q(is_active=True)
            condition &= ~Q(sender_id=request.user.id)
            condition &= Q(receiver_id=request.user.id)
            total_count = 0
            limit = 10
            offset = 0
            if 'offset' in request.data and request.data['offset']:
                offset = request.data['offset']
            if 'limit' in request.data and request.data['limit']:
                limit = request.data['limit']
            if "search_content" in request.data and request.data['search_content'] :
                or_condition = Q(is_accepted__username__icontains=request.data['search_content']) | Q(is_accepted__first_name__icontains=request.data['search_content']) | Q(is_accepted__email__icontains=request.data['search_content']) | Q(is_accepted__last_name__icontains=request.data['search_content']) 
                condition &= or_condition    
            
            total_count = FriendRequest.objects.filter(condition).count()
            query_set = FriendRequest.objects.filter(condition).order_by('-created_at')[int(offset):int(offset) + int(limit)]
            serializer = FriendRequestSerializer(query_set, many= True)
            response_content['count'] = total_count
            friend_list = []
            if serializer.data:
                for friend in serializer.data:
                    friend_list.append(friend['sender_name'])
                response_content["data"] = friend_list
            else:
                response_content['data'] = []
            return Response(response_content, status= status.HTTP_200_OK)
        except Exception as e:
            # Application failure content
            log.error("Exception in Friend list API",e)
            return Response({"error": False, "message": e, "status": 400}, status= status.HTTP_400_BAD_REQUEST)

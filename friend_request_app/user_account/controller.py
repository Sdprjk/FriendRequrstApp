import datetime
import re
import logging

from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Q 
from django.contrib.auth.models import User

log = logging.getLogger(__name__)
pattern = "\W"

class UserController():

    def createUserDetails(self,request):
        try:
            log.info("ApiCallController api CreateDetails")
            new_data={}
            if request.data:
                if 'username' in request.data and request.data['username']:
                    user_data = User.objects.filter(username__iexact=request.data['username'])
                    if user_data.exists():
                        return {"error": False, "message": 'Username already exist', "status": 400}
                    else:
                        result = re.findall(r'[\s]', request.data['username'].strip().lower())
                        if len(result)==0:
                            new_data['username'] = request.data['username'].strip().lower()
                        else:
                            return {"error": True, "message": "please provide valid username, Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only ", "status": 400}
                else:
                    new_data['username'] = request.data['email']

                if 'first_name' in request.data and request.data['first_name']:
                    new_data['first_name'] = request.data['first_name']
                
                if 'last_name' in request.data and request.data['last_name']:
                    new_data['last_name'] = request.data['last_name']
                
                if 'password' in request.data and request.data['password']:
                    new_data['password'] = make_password(request.data['password'])
                else:
                    return {"error": True, "message": "please provide password", "status": 400}
                
                if 'email' in request.data and request.data['email']:
                    user_email = User.objects.filter(Q(email__iexact=request.data['email']))
                    if user_email.exists():
                        return {"error": False, "message": 'Email already exist', "status": 400}
                    else:
                        new_data['email'] = request.data['email'].strip().lower()
                else:
                    return {"error": True, "message": "please provide email", "status": 400}
                
                if 'is_active' in request.data:  
                    new_data['is_active'] = request.data['is_active'] 
                else:
                    new_data['is_active'] = True
                return (new_data)
            else:
                return {"error": True, "message": "please provide details", "status": 400}
        except Exception as ex:
            log.error(ex)
            return {"error": True, "message": f"Exception please provide details {ex}", "status": 400}
        



    def sendRequestDetails(self,request):
        try:
            log.info("ApiCallController api sendRequestDetails")
            request_data={}
            if request.data:
                if 'receiver_id' in request.data and request.data['receiver_id']:
                    request_data['receiver_id'] = request.data['receiver_id']
                else:
                    return {"error": True, "message": "please provide receiver_id", "status": 400}
                
                request_data['sender_id'] = request.user.id
                request_data['is_rejected'] = False
                request_data['is_accepted'] = False
                request_data['is_deleted'] = False
                request_data['is_active'] = True
                request_data['created_by'] = request.user.id
                request_data['updated_by'] = request.user.id
                request_data['created_at'] = datetime.datetime.now()
                request_data['updated_at'] = datetime.datetime.now()
                return (request_data)
                
            else:
                return {"error": True, "message": "please provide details", "status": 400}
        except Exception as ex:
            log.error(ex)
            return {"error": True, "message": f"Exception please provide details {ex}", "status": 400}
        

    def acceptRequestDetails(self,request):
        try:
            log.info("ApiCallController api acceptRequestDetails")
            request_data={}
            if request.data:
                if 'sender_id' in request.data and request.data['sender_id']:
                    request_data['sender_id'] = request.data['sender_id']
                else:
                    return {"error": True, "message": "please provide sender_id", "status": 400}
                
                request_data['is_accepted'] = True
                request_data['is_active'] = False
                request_data['created_by'] = request.user.id
                request_data['updated_by'] = request.user.id
                request_data['created_at'] = datetime.datetime.now()
                request_data['updated_at'] = datetime.datetime.now()
                return (request_data)
                
            else:
                return {"error": True, "message": "please provide details", "status": 400}
        except Exception as ex:
            log.error(ex)
            return {"error": True, "message": f"Exception please provide details {ex}", "status": 400}
        

    def rejectRequestDetails(self,request):
        try:
            log.info("ApiCallController api rejectRequestDetails")
            request_data={}
            if request.data:
                if 'sender_id' in request.data and request.data['sender_id']:
                    request_data['sender_id'] = request.data['sender_id']
                else:
                    return {"error": True, "message": "please provide sender_id", "status": 400}
                
                request_data['is_rejected'] = True
                request_data['is_active'] = False
                request_data['created_by'] = request.user.id
                request_data['updated_by'] = request.user.id
                request_data['created_at'] = datetime.datetime.now()
                request_data['updated_at'] = datetime.datetime.now()
                return (request_data)
                
            else:
                return {"error": True, "message": "please provide details", "status": 400}
        except Exception as ex:
            log.error(ex)
            return {"error": True, "message": f"Exception please provide details {ex}", "status": 400}
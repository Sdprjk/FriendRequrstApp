from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from enum import Enum
# Create your models here.


class FriendRequest(models.Model):
   
    fr_id = models.AutoField(primary_key=True, db_index=True)
    receiver_id= models.ForeignKey(User,on_delete=models.CASCADE,related_name='request_receiver_id',null=True,blank=True)
    sender_id= models.ForeignKey(User,on_delete=models.CASCADE,related_name='request_sender_id',null=True,blank=True)
    is_rejected = models.BooleanField(default=False, null=True, blank=True)
    is_accepted = models.BooleanField(default=False, null=True, blank=True)
    extras= models.JSONField(default=dict, blank=True, null=True)
    is_deleted= models.BooleanField(default=False, null=True, blank=True)
    is_active= models.BooleanField(default=False, null=True, blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    created_at= models.DateTimeField(default=timezone.now, null=True, blank=True)
    updated_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='request_updated_by',null=True,blank=True)
    updated_at= models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'friend_request'  
        verbose_name = 'FriendRequest'  
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from . manager import UserManager
from django.utils import timezone


class User(AbstractUser):
    username = None
    name = models.CharField(max_length=60)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)
    gender = models.CharField(max_length=10, blank=True)
    dob = models.DateField(null=True)
    contact_no = models.CharField(max_length=10, validators=[RegexValidator(r'^[0-9]+$')])
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
class AllChats(models.Model):
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name='chat_owner')
    title=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    is_deleted=models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title


class ChatMessages(models.Model):
    chatid=models.ForeignKey(AllChats,on_delete=models.CASCADE,related_name='chat_id')
    sender = models.TextField()
    msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return self.chatid.title


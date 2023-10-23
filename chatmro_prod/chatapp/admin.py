from django.contrib import admin
from chatapp.models import User,AllChats,ChatMessages
# Register your models here.
admin.site.register(User)
admin.site.register(AllChats)
admin.site.register(ChatMessages)

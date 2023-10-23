from django.contrib import admin
from django.urls import path
from chatapp import views

urlpatterns = [
    path('', views.home,name="home"),
    path('register/', views.register,name="register"),
    path('login/', views.login_user,name="login"),
    path('logout/', views.logout_user,name="logout"),
    path('chat-list/', views.chat_screen,name="chat-list"),
    path('create-chat/', views.create_chat,name="create-chat"),
    path('chat_screen_user/<int:id>', views.chat_screen_user,name="chat_screen_user"),
    path('chat_screen_user_ajax/<int:id>', views.chat_screen_user2,name="chat_screen_user_ajax"),
]

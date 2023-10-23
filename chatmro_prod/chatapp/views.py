from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from chatapp.models import User, AllChats,ChatMessages
from django.db.models import Q
from datetime import datetime
from django.contrib import messages
from django.db import IntegrityError
import re
# from chatapp.llm import chat_llm
from chatapp.db_llm import chat_llm


def home(request):
    return render(request,'chatapp/landing_page.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        dob = request.POST['dob']
        contact_no = request.POST['contact_no']
        
        try:
            user = User.objects.create_user(name=name, email=email, password=password, dob=dob, contact_no=contact_no)
            # Redirect to login page or any other desired page after successful registration
            return redirect('login')
        except IntegrityError:
            messages.error(request, 'Email address is already registered.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    
    return render(request, 'chatapp/register.html')


def logout_user(request):
    logout(request)
    return redirect('login')
    
def login_user(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        print(user,password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid email or password.'
            return render(request, 'chatapp/login.html', {'error_message': error_message})
    
    return render(request, 'chatapp/login.html')


def create_chat(request):
    print("insdie createchat")
    user=request.user
    title=request.POST.get('title')
    newchat=AllChats.objects.create(owner=user,title=title)
    print("created chat")
    return redirect('chat-list')

@login_required(login_url='login')
def chat_screen(request):
    user = request.user
    users = User.objects.exclude(id=user.id)
    allchats = AllChats.objects.filter(Q(owner=request.user)).order_by('-created_at')
    lastchat = AllChats.objects.filter(Q(owner=request.user)).last()
    selected_chat_msg=ChatMessages.objects.filter(chatid=lastchat).order_by('created_at')
    context = {
        'user': user,
        'allchats':allchats,
        'lastchat':lastchat,
        'selected_chat_msg':selected_chat_msg
       
    }
    
    return render(request, 'chatapp/chats.html', context)

@login_required(login_url='login')
def chat_screen_user(request,id):
    user = request.user
    msg_id=None
    user_chat=AllChats.objects.filter(id=id,owner=user)
    if len(user_chat)==0:
        return redirect('chat-list') 
    if request.method == 'POST':
        sender_email=user.email
        message = request.POST.get('message')
        lastchatid = request.POST.get('chat_id')
        last_chat=AllChats.objects.get(id=lastchatid)
        chat = ChatMessages.objects.create(sender=sender_email,chatid=last_chat , msg=message)
        start_time=datetime.now()
        response=chat_llm(message)
        if '\n' in response:
            response=wrap_in_html(response)
        print("time taken:",datetime.now()-start_time)
        print(response,"chatbot response")
        # response=wrap_in_html(response)
        if response==None:
            response="Sorry ! i cant provide an answer to that"
        chatmro = ChatMessages.objects.create(sender='chatMRO',chatid=last_chat , msg=response)
        msg_id=chatmro.id
        print(msg_id,"msg_id")
    allchats = AllChats.objects.filter(Q(owner=request.user)).order_by('-created_at')
    lastchat = AllChats.objects.get(id=id)
    selected_chat_msg=ChatMessages.objects.filter(chatid=lastchat).order_by('created_at')
    selected_chat_msgid=ChatMessages.objects.filter(chatid=lastchat).order_by('-created_at')
    if msg_id==None:
        if selected_chat_msgid:
            msg_id=selected_chat_msgid[0].id
        else:
            msg_id=0
    print(msg_id,"msg_id")
    context = {
        'user': user,
        'allchats':allchats,
        'lastchat':lastchat,
        'selected_chat_msg':selected_chat_msg,
        'msg_id':msg_id
    }
    
    return render(request, 'chatapp/chats.html', context)

def chat_screen_user2(request,id):
    user = request.user
    msg_id=None
    print(id,"idddd",user,"useruser")

    if request.method == 'POST':
        sender_email=user.email
        message = request.POST.get('message')
        lastchatid = request.POST.get('chat_id')
        last_chat=AllChats.objects.get(id=lastchatid)
        chat = ChatMessages.objects.create(sender=sender_email,chatid=last_chat , msg=message)
        start_time=datetime.now()
        response=chat_llm(message)
        if '(https' in response :
            all_urls=re.findall(r'\(https.*\)',response)
            for ma in all_urls:
                url=ma.split('(')[1].replace(')','')
                response=response.replace(f"({url})",f'<a style="font-size:10px;" href={url} target="_blank"> Click to open</a>')
        
        response='''<div style="max-width: 100%;  overflow-x: auto;"><pre  style="white-space: pre-wrap; padding: 10px;
                             font-size: 16px; font-family: 'Roboto', sans-serif;">'''+response+'</pre></div>'
        
        # if '\n' in response:
        #     response=wrap_in_html(response)
        print("time taken:",datetime.now()-start_time)
        print(response,"chatbot response")
        
        if response==None:
            response="Sorry ! i cant provide an answer to that"
        chatmro = ChatMessages.objects.create(sender='chatMRO',chatid=last_chat , msg=response)
        msg_id=chatmro.id
        print(msg_id,"msg_id")
    allchats = AllChats.objects.filter(Q(owner=request.user)).order_by('-created_at')
    lastchat = AllChats.objects.get(id=id)
    selected_chat_msg=ChatMessages.objects.filter(chatid=lastchat).order_by('created_at')
    selected_chat_msgid=ChatMessages.objects.filter(chatid=lastchat).order_by('-created_at')
    if msg_id==None:
        if selected_chat_msgid:
            msg_id=selected_chat_msgid[0].id
        else:
            msg_id=0
    print(msg_id,"msg_id")
    response_data = {'response': response}

    # Return the JSON response
    return JsonResponse(response_data)



def wrap_in_html(text):
    lines = text.split('\n')
    html_lines = []

    in_list = False
    for line in lines:
        if line.startswith("- "):
            if not in_list:
                in_list = True
                html_lines.append("<ul>")
            html_lines.append("<li>{}</li>".format(line[2:].strip()))
        else:
            if in_list:
                in_list = False
                html_lines.append("</ul>")
            html_lines.append("<p>{}</p>".format(line.strip()))

    if in_list:
        html_lines.append("</ul>")

    html_content = '\n'.join(html_lines)
    return html_content

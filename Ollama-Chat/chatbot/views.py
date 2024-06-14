from django.shortcuts import render, redirect
from django.http import JsonResponse
import ollama

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


def ask_openai(messages):
    response = ollama.chat(
        model = "phi3",
        messages=messages
    )
    return response['message']['content']

def list_chat(chats,message,request):
    messages=[{'role':'system',"content":"Your an Help assistant name JARVIS and you reply like Tony stark jarvis"}]
    for chat in chats:
        if chat.user==request.user:
            messages.append({"role":"user","content":chat.message})
            messages.append({"role":"assistant",'content':chat.response})

    messages.append({'role':'user',"content":message})

    return messages
@csrf_exempt
# Create your views here.
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        user_input = request.POST.get('message')
        list_chats=list_chat(chats,user_input,request)
        print(list_chats)
        response = ask_openai(list_chats)
        chat = Chat(user=request.user, message=user_input, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': user_input, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})

@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

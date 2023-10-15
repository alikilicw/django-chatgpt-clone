from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai, os

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat


from django.utils import timezone

openai_api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = openai_api_key

def ask_openai(message):
    response = openai.Completion.create(
        model = os.getenv('AI_MODEL'),
        prompt = message,
        max_tokens = 150,
        n = 1,
        stop = None,
        temperature = 0.7
    )
    print(response)
    answer = response.choices[0].text.strip()
    return answer
    

def chatbot(request):
    if request.user.is_anonymous:
        return redirect('login')

    chats = Chat.objects.filter(user = request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()

        return JsonResponse({'message': message, 'response': response})

    return render(request, "chatbot.html", {'chats': chats})


def login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def register(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except Exception as er:
                error_message = 'Error creating account'
                print("sıkıntı", er)
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Password dont match"
            return render(request, 'register.html', {'error_message': error_message})

    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
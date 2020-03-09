from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.core.mail import send_mail
import random
import re
from .forms import SignUpForm
from .models import Profile, Like, Comment, StoryView, Reply, Story, Blog, Image
from django.contrib.auth.models import User
from django.contrib import auth, messages


def home(request):
    return render(request, 'sayonestories/Home.html', context={})


class RegisterView(View):

    def get(self, request):
        form = SignUpForm()
        return render(request, 'sayonestories/Registration.html', context={'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)

            otp = random.randint(10000, 90000)
            email_body = f"""
                   Hi User,

                   use this code {str(otp)} to verify your Sayonestories account

                   Thanks for registering with us

                   Sincerely,
                   Sayonestories Team
                   """
            send_mail(
                'Account verification Sayonestories',
                email_body,
                'testusersayone@gmail.com',
                [user.email],
                fail_silently=False,
            )
            return render(request, 'sayonestories/Register_Confirm.html',
                          context={'username': user.username, 'otp': otp})
        else:
            return render(request, 'sayonestories/Registration.html', context={'form': form})


class RegisterVerify(View):
    def get(self, request):
        return render(request, 'sayonestories/Register_Confirm.html', context={})

    def post(self, request):
        user_name = request.POST.get('username')
        otp = request.POST.get('otp2')
        enteredotp = request.POST.get('enteredotp')

        if str(enteredotp) == str(otp):
            user_obj = get_object_or_404(User, username=user_name)
            profile_obj = get_object_or_404(Profile,user=user_obj)
            profile_obj.verified = True
            profile_obj.save()
            return redirect('login')
        else:
            return render(request, 'sayonestories/Register_Confirm.html', context={'error': 'please check your code'})


def user_home_page(request):
    return render(request, 'sayonestories/UserHome.html', context={})


def username_email_login(request):
    print('here1')
    flag = ''
    username = request.POST.get('username')
    password = request.POST.get('password')

    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    if re.search(regex, username):
        flag = 'mail'
    else:
        flag = 'username'

    if flag == 'mail':
        queryset = get_object_or_404(User, email=username)
        user_name = queryset.username
        profile_obj = get_object_or_404(Profile, user=queryset)
        if profile_obj.verified == False:
            return redirect('Verify_Register')
        else:
            user = auth.authenticate(username=user_name, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('userhome')
            else:
                messages.success(request, 'email or password is incorrect')
                return redirect('/accounts/login/')


    else:
        print('here2')
        queryset = get_object_or_404(User, username=username)
        print('user',queryset)
        profile_obj = get_object_or_404(Profile, user=queryset)
        print(profile_obj)
        if profile_obj.verified == False:
            return redirect('Verify_Register')
        else:
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('userhome')
            else:
                messages.success(request, 'username or password is incorrect')
                return redirect('/accounts/login/')

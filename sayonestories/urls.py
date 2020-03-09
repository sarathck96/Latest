from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('user_home',views.user_home_page, name='userhome'),
    path('Register_page', views.RegisterView.as_view(), name='Register'),
    path('Register_verify', views.RegisterVerify.as_view() ,name='Verify_Register'),
    path('user_email',views.username_email_login, name='Username_Email_Login'),
]

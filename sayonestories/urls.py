from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('user_home',views.user_home_page, name='userhome'),
    path('Register_page', views.RegisterView.as_view(), name='Register'),
    path('Register_verify', views.RegisterVerify.as_view() ,name='Verify_Register'),
    path('user_email',views.username_email_login, name='Username_Email_Login'),
    path('AddStory',views.AddStoryView.as_view(), name='AddStoryView'),
    path('AddBlog', views.addblog, name='Add_Blog'),
    path('AddGallery',views.addgallery, name='Add_Gallery'),
    path('StoryDetail/<int:id>/', views.story_detail_page, name='Story_Detail_Page'),
]

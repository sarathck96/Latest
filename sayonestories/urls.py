from django.urls import path

from . import views
from .forms import EmailValidationOnForgotPassword
from django.contrib.auth import views as auth_views

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
    path('like_story/<int:story_id>/', views.like_story, name='like_story'),
    path('addfav/<int:story_id>/',views.add_to_fav,name='add_to_fav'),
    path('addreply',views.add_reply, name='add_reply'),
    path('Blogs_List', views.BlogsList.as_view(), name='BlogList'),
    path('Events_List', views.EventList.as_view(), name='EventList'),
    path('Gallery_List', views.GalleryList.as_view(), name='GalleryList'),
    path('All_Stories', views.AllStoriesList.as_view(), name='AllStoriesList'),
    path('User_Favourites', views.UserFavourites.as_view(), name='UserFavourites'),
    path('User_Stories',views.UserStories.as_view(), name='UserStories'),
    path('User_Profile/<int:pk>/', views.UserProfilePage.as_view(), name='UserProfile'),
    path('User_Profile_Update/<int:pk>/', views.UserProfileUpdate.as_view() , name='ProfileUpdate'),
    path('Story_Detail2/<int:id>/',views.story_detail_page2, name='StoryDetail2'),
    path('Top_Authors', views.top_authors, name='TopAuthors'),
    path('Filter', views.filter ,name='Filter'),
    path('Delete_Story/<int:pk>/', views.DeleteStory.as_view(), name='DeleteStory'),
    path('Edit_Story_Page/<int:id>/', views.edit_story_page , name='EditStoryPage'),
    path('Edit_Story', views.edit_story , name='EditStory'),
    path('Update_Gallery/<int:story_id>/', views.updategallery ,name='UpdateGallery'),
    path('Update_Profile_pic', views.update_profile_pic, name='UpdateProfilePic'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(form_class=EmailValidationOnForgotPassword),
         name='password_reset'),

]

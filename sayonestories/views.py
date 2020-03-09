from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.core.mail import send_mail
import random
import re
from .forms import SignUpForm, StoryAddForm, AddBlogForm, MultiUploadForm, AddCommentForm, ReplyForm
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
            profile_obj = get_object_or_404(Profile, user=user_obj)
            profile_obj.verified = True
            profile_obj.save()
            return redirect('login')
        else:
            return render(request, 'sayonestories/Register_Confirm.html', context={'error': 'please check your code'})


def user_home_page(request):
    top_events = Story.objects.filter(stype=Story.EVENT).filter(status=Story.PUBLISH).order_by('-likes')[:3]
    top_blogs = Story.objects.filter(stype=Story.BLOG).filter(status=Story.PUBLISH).order_by('-likes')[:3]
    top_gallery = Story.objects.filter(stype=Story.GALLERY).filter(status=Story.PUBLISH).order_by('-likes')[:3]

    context = {'events':top_events,'blogs':top_blogs,'gallery':top_gallery}
    return render(request, 'sayonestories/UserHome.html', context)


def username_email_login(request):
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

        queryset = get_object_or_404(User, username=username)

        profile_obj = get_object_or_404(Profile, user=queryset)

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


class AddStoryView(View):
    form_class = StoryAddForm
    initial = {'key': 'value'}
    template_name = 'sayonestories/AddStory.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user
            story.save()

            if story.stype in [Story.BLOG, Story.EVENT]:
                form1 = AddBlogForm()
                return render(request, 'sayonestories/AddStory.html', context={'story': story, 'form1': form1})
            else:
                form2 = MultiUploadForm()
                return render(request, 'sayonestories/AddStory.html', context={'story': story, 'form2': form2})
        else:
            return render(request, self.template_name, {'form': form})


def addblog(request):
    story_id = request.POST.get('storyid')
    story_obj = get_object_or_404(Story, id=story_id)

    if request.method == 'POST':
        form = AddBlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.story = story_obj
            blog.save()
            return redirect('userhome')
        else:
            return render(request, 'sayonestories/AddStory.html', context={'form1': form})
    else:
        return render(request, 'sayonestories/AddStory.html', context={})


def addgallery(request):
    story_id = request.POST.get('storyid')
    story_obj = get_object_or_404(Story, id=story_id)

    if request.method == 'POST':

        form = MultiUploadForm(request.POST, request.FILES)
        if form.is_valid():
            for each in form.cleaned_data['file']:
                Image.objects.create(file=each, story=story_obj)

        return redirect('userhome')
    else:
        form = MultiUploadForm()
        return render(request, 'sayonestories/AddStory.html', context={'form2': form})


def story_detail_page(request, id):
    """loads all the details regarding the selected story .details include story title,author,date created and
    substory details .if substory is blog or event the details include title,image and description .if substory is
    image gallery details include title and images """

    views = record_view(request, id)

    story_obj = Story.objects.filter(id=id)[0]

    story_obj.views = views

    story_obj.save()

    form2 = ReplyForm()

    form = AddCommentForm()
    comments = Comment.objects.filter(story=story_obj)

    already_liked = ''
    if Like.objects.filter(user=request.user).filter(story=story_obj):
        already_liked = 'yes'
    else:
        already_liked = 'no'

    if story_obj.stype in [Story.BLOG, Story.EVENT]:

        context = {'blog': 'blog', 'story': story_obj,
                   'liked': already_liked, 'form': form, 'comments': comments, 'form2': form2}
        return render(request, 'sayonestories/Story_Detail_Page.html', context)
    else:
        sub_story_object = story_obj.image_story.all()
        print(sub_story_object)

        for item in sub_story_object:
            print(item.file)
        context1 = {'substory': sub_story_object, 'story': story_obj, 'liked': already_liked, 'form': form,
                    'comments': comments, 'form2': form2}
        return render(request, 'sayonestories/Story_Detail_Page.html', context=context1)


def record_view(request, story_id):
    story_obj = get_object_or_404(Story, pk=story_id)

    if not StoryView.objects.filter(story=story_obj, session=request.session.session_key):
        view = StoryView.objects.create(story=story_obj, session=request.session.session_key)
        view.save()

    number_of_visits = StoryView.objects.filter(story=story_obj).count()

    return number_of_visits
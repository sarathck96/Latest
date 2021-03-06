import random
import re

from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView, DeleteView

from .forms import (AddBlogForm, AddCommentForm, MultiUploadForm, ReplyForm,
                    SignUpForm, StoryAddForm, UpdateProfilePicForm, MultiUploadForm2)
from .models import (Blog, Comment, Favourite, Image, Like, Profile, Reply,
                     Story, StoryView)


def home(request):
    top_events = Story.objects.filter(stype=Story.EVENT).filter(status=Story.PUBLISH).order_by('-likes')[:3]
    top_blogs = Story.objects.filter(stype=Story.BLOG).filter(status=Story.PUBLISH).order_by('-likes')[:3]
    top_gallery = Story.objects.filter(stype=Story.GALLERY).filter(status=1).order_by('-likes')[:3]

    context = {'events': top_events, 'blogs': top_blogs, 'gallery': top_gallery}
    return render(request, 'sayonestories/Home.html', context)


class RegisterView(View):

    def get(self, request):
        form = SignUpForm()
        return render(request, 'sayonestories/Registration.html', context={'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            otp = random.randint(10000, 90000)
            email_body = f"""
                   Hi User,

                   use this code {str(otp)} to verify your Sayonestories account

                   Thanks for registering with us

                   Sincerely,
                   Sayonestories Team
                   """
            Profile.objects.create(user=user, otp=otp)
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

@login_required(login_url='/accounts/login/')
def user_home_page(request):
    top_events = Story.objects.filter(stype=Story.EVENT).filter(status=Story.PUBLISH).order_by('-likes')[:3]
    top_blogs = Story.objects.filter(stype=Story.BLOG).filter(status=Story.PUBLISH).order_by('-likes')[:3]
    top_gallery = Story.objects.filter(stype=Story.GALLERY).filter(status=Story.PUBLISH).order_by('-likes')[:3]

    context = {'events': top_events, 'blogs': top_blogs, 'gallery': top_gallery}
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


class AddStoryView(LoginRequiredMixin,View):
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

@login_required(login_url='/accounts/login/')
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

@login_required(login_url='/accounts/login/')
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

@login_required(login_url='/accounts/login/')
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

@login_required(login_url='/accounts/login/')
def like_story(request, story_id):
    """ allows the user to like a story .checks whether the user have already liked the story .if already liked alerts
     the user that story is liked ,else increments the like count by one. story_id is unique id of story used to check
     whether user have already liked the story """

    story = get_object_or_404(Story, id=story_id)

    can_like = ''
    if story.user == request.user:
        can_like = 'own'

    elif Like.objects.filter(user=request.user).filter(story=story):
        Story.objects.filter(id=story_id).update(likes=F('likes') - 1)
        Like.objects.filter(story=story).delete()
        can_like = 'no'
    else:
        Story.objects.filter(id=story_id).update(likes=F('likes') + 1)
        like = Like.objects.create(user=request.user, story=story)
        can_like = 'yes'
    print('can_like', can_like)

    data = {'is_valid': can_like}
    return JsonResponse(data)

@login_required(login_url='/accounts/login/')
def add_to_fav(request, story_id):
    print('call in fav')
    story_obj = Story.objects.get(id=story_id)
    fav_obj = Favourite.objects.filter(user=request.user, story=story_obj)

    if len(fav_obj) == 0:
        new_fav_obj = Favourite.objects.create(user=request.user, story=story_obj)
        return JsonResponse({'added': 'yes'})

    else:

        return JsonResponse({'added': 'no'})

@login_required(login_url='/accounts/login/')
def add_reply(request):
    if request.POST.get('action') == 'post':
        story_id = request.POST.get('story_id')
        comm_id = request.POST.get('comment_id')
        reply_text = request.POST.get('reply_text')
        story_id2 = request.POST.get('story_id2')

    if story_id2 is None:

        story_obj = Story.objects.filter(id=story_id)[0]

        comment_obj = Comment.objects.filter(id=comm_id)[0]
        user_replied = request.user

        reply_obj = Reply.objects.create(reply=reply_text, comment=comment_obj, user=user_replied)

        response_list = []
        for item in comment_obj.reply_to_comment.all():
            temp_dict = {}
            temp_dict['reply'] = item.reply
            temp_dict['replied_by'] = item.user.get_full_name()

        return JsonResponse({'response': temp_dict, 'divid': comm_id}, safe=False)
    else:
        print('comment section')
        story_obj = Story.objects.filter(id=story_id2)[0]
        user_commented = request.user
        comment = request.POST.get('comment')
        comment_obj = Comment.objects.create(user=user_commented, story=story_obj, comment=comment)

        temp_dict2 = {}
        temp_dict2['comment'] = comment_obj.comment
        temp_dict2['user_commented'] = comment_obj.user.get_full_name

        temp_dict2['comment_id'] = comment_obj.id
        temp_dict2['story_id'] = story_id2

        temp_dict2['date_commented'] = comment_obj.created

        return JsonResponse({'response': temp_dict2, 'comment': 'com'})


class BlogsList(LoginRequiredMixin,ListView):
    template_name = 'sayonestories/BlogList.html'
    context_object_name = 'blog_list'
    queryset = Story.objects.filter(stype=Story.BLOG, status=Story.PUBLISH)


class EventList(LoginRequiredMixin,ListView):
    template_name = 'sayonestories/EventsList.html'
    context_object_name = 'event_list'
    queryset = Story.objects.filter(stype=Story.EVENT, status=Story.PUBLISH)


class GalleryList(LoginRequiredMixin,ListView):
    template_name = 'sayonestories/GalleryList.html'
    context_object_name = 'gallery_list'
    queryset = Story.objects.filter(stype=Story.GALLERY, status=Story.PUBLISH)


class AllStoriesList(LoginRequiredMixin,ListView):
    template_name = 'sayonestories/AllStories.html'
    context_object_name = 'stories'
    queryset = Story.objects.filter(status=Story.PUBLISH)
    paginate_by = 2


class UserFavourites(LoginRequiredMixin,ListView):
    template_name = 'sayonestories/UserFavourites.html'
    context_object_name = 'favourites'

    def get_queryset(self):
        story_list = []
        favourite_list = Favourite.objects.filter(user=self.request.user)
        for item in favourite_list:
            story_list.append(item.story)
        return story_list


class UserStories(LoginRequiredMixin,ListView):
    template_name = 'sayonestories/UserStories.html'
    context_object_name = 'userstories'

    def get_queryset(self):
        return Story.objects.filter(user=self.request.user).filter(status=Story.PUBLISH)


class UserProfilePage(LoginRequiredMixin,DetailView):

    def get(self, request, *args, **kwargs):
        details = get_object_or_404(User, pk=kwargs['pk'])
        story_obj = Story.objects.filter(user=self.request.user)
        profile_obj = get_object_or_404(Profile, user=self.request.user)
        ff = UpdateProfilePicForm()
        context = {'profiledetails': details, 'count': story_obj.count, 'pic': profile_obj.profile_pic, 'form': ff}
        return render(request, 'sayonestories/UserProfile.html', context)


class UserProfileUpdate(LoginRequiredMixin,UpdateView):
    model = User
    template_name = 'sayonestories/UserProfileEdit.html'
    fields = ('first_name', 'last_name')
    success_url = reverse_lazy('userhome')


def story_detail_page2(request, id):
    story_obj = get_object_or_404(Story, id=id)
    comments = Comment.objects.filter(story=story_obj)
    if story_obj.stype in [Story.EVENT, Story.BLOG]:

        context = {'blog': 'blog', 'story': story_obj, 'comments': comments}
        return render(request, 'sayonestories/Story_Detail_Page2.html', context)
    else:
        sub_story_object = story_obj.image_story.all()

        context1 = {'substory': sub_story_object, 'story': story_obj, 'comments': comments}
        return render(request, 'sayonestories/story_detail_page2.html', context=context1)

@login_required(login_url='/accounts/login/')
def top_authors(request):
    users_and_like = []
    all_users = User.objects.all()
    for user in all_users:
        like_count = 0
        story_obj = Story.objects.filter(user=user)
        for story in story_obj:
            like_count = like_count + story.likes
        users_and_like.append(tuple((user.username, like_count)))

    top_users = sorted(users_and_like, key=lambda t: t[1], reverse=True)[:3]

    top_authors = []
    for i in range(0, 3):
        user = User.objects.filter(username=top_users[i][0])[0]
        sayoneuser = Profile.objects.filter(user=user)[0]
        temp_dict = {}
        temp_dict['pic'] = sayoneuser.profile_pic
        temp_dict['name'] = sayoneuser.user.get_full_name()
        temp_dict['likes'] = top_users[i][1]
        top_authors.append(temp_dict)

    return render(request, 'sayonestories/Top_Authors.html', context={'authors': top_authors})

@login_required(login_url='/accounts/login/')
def filter(request):
    param = request.POST.get('filterparam')

    results = Story.objects.filter(Q(title__icontains=param))
    context = {'stories': results}
    if len(results) == 0:
        results = Blog.objects.filter(Q(description__icontains=param))
        results2 = ''
        for item in results:
            results2 = Story.objects.filter(title=item)

        context = {'stories': results2}

    return render(request, 'sayonestories/FilteredResults.html', context)


class DeleteStory(LoginRequiredMixin,DeleteView):
    model = Story
    template_name = 'sayonestories/Delete_Story_Confirm.html'
    success_url = reverse_lazy('UserStories')

@login_required(login_url='/accounts/login/')
def edit_story_page(request, id):
    story_obj = Story.objects.get(id=id)
    story_type = story_obj.stype
    story_title = story_obj.title

    if story_type in [Story.EVENT, Story.BLOG]:

        context = {'blog': 'blog', 'title': story_title, 'description': story_obj.blog_story.description,
                   'pic': story_obj.blog_story.pic, 'id': story_obj.id}
        return render(request, 'sayonestories/Story_Edit_Page.html', context)

    else:

        form = MultiUploadForm2()
        context = {'title': story_title, 'id': story_obj.id, 'story': story_obj, 'form': form}
        return render(request, 'sayonestories/Story_Edit_Page.html', context)

@login_required(login_url='/accounts/login/')
def edit_story(request):
    story_id = request.POST.get('id')

    story_title = request.POST.get('title')
    story_description = request.POST.get('description')
    story_description2 = request.POST.get('description2')

    if not story_description2 == None:
        story = Story.objects.filter(id=story_id).first()
        image_story = Image.objects.filter(story=story).first()
        image_story.description = story_description2
        image_story.save()

    pic = ''
    if request.FILES.get('newpic'):
        story_pic = request.FILES.get('newpic')
        pic = 'yes'
    else:
        pic = 'no'

    story_obj = Story.objects.filter(id=story_id).first()
    story_obj.title = story_title
    story_obj.save()

    if story_obj.stype in [Story.EVENT, Story.BLOG]:
        blog_obj = Blog.objects.filter(story=story_obj).first()
        blog_objdescription = story_description
        if pic == 'yes':
            blog_obj.pic = story_pic
        blog_obj.save()
        return redirect('Story_Detail_Page', id=story_id)
    else:
        return redirect('Story_Detail_Page', id=story_id)

@login_required(login_url='/accounts/login/')
def updategallery(request, story_id):
    story_id = story_id
    story_obj = Story.objects.filter(id=story_id)[0]
    if request.method == 'POST':
        form2 = MultiUploadForm2()

        form = MultiUploadForm2(request.POST, request.FILES)
        if form.is_valid():
            for each in form.cleaned_data['file']:
                Image.objects.create(file=each, story=story_obj)
        context = {'title': story_obj.title, 'id': story_obj.id, 'story': story_obj, 'form': form2}
        return render(request, 'sayonestories/Story_Edit_Page.html', context)
    else:
        context = {'title': story_obj.title, 'id': story_obj.id, 'story': story_obj,'form':form}
        return render(request, 'sayonestories/story_edit_page.html', context)

@login_required(login_url='/accounts/login/')
def update_profile_pic(request):
    error_message = ''
    profile_pic = request.FILES.get('pic')
    if profile_pic == None:
        error_message = 'please select an image'
        return render(request,'sayonestories/UserProfile.html',context={'error':error_message})
    else:
        obj = Profile.objects.get(user=request.user)
        obj.profile_pic = profile_pic
        obj.save()
        return redirect('UserProfile',pk=request.user.id)

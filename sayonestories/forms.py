from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from multiupload.fields import MultiFileField

from .models import Blog, Comment, Image, Profile, Reply, Story


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(validators=[MinLengthValidator(5)])

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'username': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),

        }

        labels = {
            'first_name': '*First Name',
            'last_name': '*Last Name',
            'email': '*MailID',
            'password1': '*PASSWORD',
            'password2': '*CONFIRM PASSWORD',

        }


class StoryAddForm(forms.ModelForm):
    class Meta:
        model = Story
        exclude = ('user', 'likes', 'status', 'views')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'stype': forms.Select(attrs={'class': 'form-control'}),

        }

        labels = {
            'title': '*Story Title',
            'stype': '*Story Type',

        }


class AddBlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        exclude = ('story',)
        widgets = {
            'pic': forms.FileInput(attrs={'class': 'form-control-file border'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'cols': 15}),
        }

        labels = {
            'pic': '*Add Image',
            'description': '*Content'
        }


class MultiUploadForm(forms.ModelForm):
    file = MultiFileField(min_num=1, max_num=4, max_file_size=1024 * 1024 * 5)

    class Meta:
        exclude = ('story',)
        model = Image

    labels = {
        'file': '*Images',
        'description': '*Description',
    }


class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('user', 'story',)

        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'id': 'comm', 'cols': 15, 'rows': 3})

        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ('reply',)

        widgets = {
            'reply': forms.Textarea(attrs={'class': 'form-control', 'id': 'reply-text', 'rows': 3, 'cols': 15})

        }


class UpdateProfilePicForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_pic',)

        widgets = {
            forms.FileInput(attrs={'class': 'form-control-file border'}),
        }


class MultiUploadForm2(forms.ModelForm):
    file = MultiFileField(min_num=1, max_num=4, max_file_size=1024 * 1024 * 5)

    class Meta:
        exclude = ('story', 'description')
        model = Image

    labels = {
        'file': '*Images',

    }


class EmailValidationOnForgotPassword(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = ("There is no user registered with the specified E-Mail address.")
            self.add_error('email', msg)
        return email

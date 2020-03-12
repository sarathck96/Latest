from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import models
from django.forms import Textarea, TextInput

from .models import (Blog, Comment, Favourite, Image, Like, Profile, Reply,
                     Story)


class MyUserAdmin(UserAdmin):
    ordering = ('-date_joined',)
    list_display = ('username', 'email', 'date_joined', 'first_name', 'last_name', 'is_staff')


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


def make_published(modeladmin, request, queryset):
    queryset.update(status=1)


make_published.short_description = "Mark selected stories as published"


class StoryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 8, 'cols': 10})},
    }
    list_display = ['title', 'stype', 'likes', 'status', 'created',
                    'user']
    list_filter = ['likes', 'created', 'status']

    actions = [make_published]


admin.site.register(Story, StoryAdmin)


class BlogAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 15, 'cols': 80})},

    }
    list_display = ['story', 'pic']
    list_display_links = ['story']


admin.site.register(Blog, BlogAdmin)


class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'story']
    list_filter = ['user']


admin.site.register(Like, LikeAdmin)


class CommentsAdmin(admin.ModelAdmin):
    list_display = ['comment', 'story', 'user', 'created']
    list_filter = ['user', 'created']
    # list_editable = ['comment']


admin.site.register(Comment, CommentsAdmin)


class ImagesAdmin(admin.ModelAdmin):
    list_display = ['file', 'story']


admin.site.register(Image, ImagesAdmin)

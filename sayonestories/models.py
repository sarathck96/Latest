from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from upload_validator import FileTypeValidator


class DateModel(models.Model):
    """
       An abstract base class model that provides date field
       """
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Profile(models.Model):
    """
   Model for storing details related to user that cannot be stored in Django's User model
   Related to auth.User model
   """

    profile_pic = models.ImageField(upload_to='images', default='images/default_pic.jpg', blank=True, null=True,
                                    validators=[FileTypeValidator(
                                        allowed_types=[
                                            'image/jpeg', 'image/png']
                                    )]
                                    )
    user = models.OneToOneField(
        User, related_name='sayone_user', on_delete=models.CASCADE)

    otp = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Profile'

    def __str__(self):
        return self.user.username


class Story(DateModel):
    """
   Stores a single Story entry.
   Related to auth.User
    """

    EVENT = 0
    BLOG = 1
    GALLERY = 2

    DRAFT = 0
    PUBLISH = 1

    STORY_TYPE_CHOICES = (
        (EVENT, 'Event'),
        (BLOG, 'Blog'),
        (GALLERY, 'Gallery')
    )

    STATUS_CHOICES = (
        (DRAFT, 'Draft'),
        (PUBLISH, 'Publish')
    )

    title = models.TextField(max_length=500)
    stype = models.IntegerField(choices=STORY_TYPE_CHOICES, default=EVENT)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    user = models.ForeignKey(
        User, related_name='story_user', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Story'

    def __str__(self):
        return self.title


class Blog(models.Model):
    """
   This model stores a single Blog entry.
   Related to  Story model
   """
    pic = models.ImageField(upload_to='images')
    description = models.TextField(max_length=5000)
    story = models.OneToOneField(
        Story, on_delete=models.CASCADE, related_name='blog_story')

    class Meta:
        verbose_name_plural = 'Blog'

    def __str__(self):
        return self.story.title


class Image(models.Model):
    """
   This model stores images for image gallery
   Related to Story model
   """

    file = models.ImageField(upload_to='images')
    description = models.TextField(max_length=5000, default='gallery')
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name='image_story')

    class Meta:
        verbose_name_plural = 'Image Gallery'

    def __str__(self):
        return self.story.title


class Like(DateModel):
    """
   This model stores single like entry
   Related to Story model and auth.User model
   """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Like'

    def __str__(self):
        return self.user.username


class Comment(DateModel):
    """
   This model stores single comment entry
   Related to sayonestories.Story and auth.User model
   """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_comment')
    comment = models.TextField(max_length=2000)

    class Meta:
        verbose_name_plural = 'Comment'

    def __str__(self):
        return self.comment


class StoryView(DateModel):
    """
       This model stores story and session detail of user inorder to track number of views for a particular story.
       Related to: model:'sayonestories.Story'.
       """
    story = models.ForeignKey(Story, related_name='storyviews', on_delete=models.CASCADE)
    session = models.CharField(max_length=100)


class Reply(DateModel):
    """
       This model stores single entry of reply for a comment.
       Related to :model:'sayonestories.Comment' and :model:'auth.User'.
       """

    reply = models.TextField(max_length=2000)
    comment = models.ForeignKey(Comment, related_name='reply_to_comment', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reply')

    class Meta:
        verbose_name_plural = 'Reply'

    def __str__(self):
        return self.reply


class Favourite(models.Model):
    """
   This model stores single entry of a user's favourite story
   Related to :model:'sayonestories.Story' and :model:'auth.User'.
   """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_fav')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='story_fav')

    class Meta:
        verbose_name_plural = 'Favourite'

    def __str__(self):
        return self.story.title

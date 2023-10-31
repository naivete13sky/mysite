from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from DjangoUeditor.models import UEditorField


class Post(models.Model):
    STATUS_CHOICES = (('draft', 'Draft'), ('published', 'Published'))
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    # body = models.TextField()
    body = UEditorField('内容', default='', width=950, height=280, imagePath='media/images/',
                               filePath='media/files/')

    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')


    class Meta:
        ordering = ('-publish',)


    def __str__(self):
        return self.title

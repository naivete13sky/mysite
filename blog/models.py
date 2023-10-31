from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from DjangoUeditor.models import UEditorField
from taggit.models import TagBase,GenericTaggedItemBase
from django.utils.text import slugify
from django.utils.translation import gettext, gettext_lazy as _
from taggit.managers import TaggableManager
from django.urls import reverse


class MyTagForPost(TagBase):
    # 这一步是关键，要设置allow_unicode=True，这样这个字段才能支持中文
    slug = models.SlugField(verbose_name=_("slug"), unique=True, max_length=100, allow_unicode=True)

    # 这个方法也是要覆盖的，它是用来计算slug的，也是添加allow_unicode=True参数
    def slugify(self, tag, i=None):
        slug = slugify(tag, allow_unicode=True)
        if i is not None:
            slug += "_%d" % i
        return slug

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        app_label = "taggit"


class TaggedWhateverForPost(GenericTaggedItemBase):
    # 把我们自定义的模型类传进来，它就能知道如何处理
    tag = models.ForeignKey(
        MyTagForPost,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (('draft', 'Draft'), ('published', 'Published'))
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    # body = models.TextField()
    body = UEditorField('内容', default='', width=950, height=280, imagePath='blog/post/images/',
                               filePath='blog/post/files/')

    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    tags = TaggableManager(through=TaggedWhateverForPost)


    class Meta:
        ordering = ('-publish',)


    def __str__(self):
        return self.title
    
    objects = models.Manager()  # 默认的管理器
    published = PublishedManager()  # 自定义管理器

    def get_absolute_url(self):
        return reverse('blog:PostDetailView', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)
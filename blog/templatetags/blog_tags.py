from django import template
from ..models import Post,MyTagForPost,TaggedWhateverForPost
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown




register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]




@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

@register.simple_tag
def get_tags_count():
    # result = TaggedWhatever.objects.values('tag_id').order_by('tag_id').annotate(count=Count('tag_id')).order_by('count')
    result = TaggedWhateverForPost.objects.values('tag_id').annotate(count=Count('tag_id')).order_by('-count')
    print(result,type(result))

    tag_list=[]
    for each in result:
        # print(each["tag_id"],each["count"])
        tag_one=MyTagForPost.objects.get(id=each["tag_id"])
        tag_list.append((tag_one.id,tag_one.name,tag_one.slug,each["count"]))

    return tag_list
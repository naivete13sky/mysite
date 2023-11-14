from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator

from .models import Post, Comment,MyTagForPost
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView,DetailView
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm,SearchForm
from taggit.models import Tag
from django.db.models import Count, Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from django.contrib.auth.decorators import login_required

from casbin_adapter.enforcer import enforcer
import functools


#写了一个带参数的装饰器，用在cretview上面，可以先判断权限。
def casbin_permission(casbin_obj,casbin_act):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request,*args, **kwargs):
            # 判断权限
            sub = request.user.username  # 想要访问资源的用户
            obj = casbin_obj  # 将要被访问的资源
            act = casbin_act # 用户对资源进行的操作
            print('sub,obj,act:', sub, obj, act)
            if enforcer.enforce(sub, obj, act):
                pass
                print("权限通过！")
                return func(request, *args, **kwargs)
            else:
                return HttpResponse("您无此权限！请联系管理员！")

        return wrapper
    return decorator


@login_required
def post_list(request,tag_slug=None):
    object_list = Post.published.all()

    tag = None
    print("tag_slug:", tag_slug)
    if tag_slug:
        # tag = get_object_or_404(Tag, slug=tag_slug)
        # 从MyTag对应的数据库表里查询tag
        tag = get_object_or_404(MyTagForPost, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])



    paginator = Paginator(object_list, 3)  # 每页显示3篇文章
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是一个整数就返回第一页
        posts = paginator.page(1)
    except EmptyPage:
        # 如果页数超出总页数就返回最后一页
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})

# @method_decorator(login_required, name='dispatch')
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 10
    template_name = 'blog/post/PostListView.html'

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        left_has_more = False
        right_has_more = False
        current_page = page_obj.number
        if current_page <= around_count + 2:
            left_range = range(1, current_page)
        else:
            left_has_more = True
            left_range = range(current_page - around_count, current_page)

        if current_page >= paginator.num_pages - around_count - 1:
            right_range = range(current_page + 1, paginator.num_pages + 1)
        else:
            right_has_more = True
            right_range = range(current_page + 1, current_page + around_count + 1)

        pagination_data = {
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'left_range': left_range,
            'right_range': right_range
        }
        return pagination_data

    def get_context_data(self, **kwargs):  # 重写get_context_data方法
        # 很关键，必须把原方法的结果拿到
        context = super().get_context_data(**kwargs)
        field_verbose_name = [Post._meta.get_field('id').verbose_name,
                                  Post._meta.get_field('title').verbose_name,
                                  Post._meta.get_field('author').verbose_name,
                                  ]
        context['field_verbose_name'] = field_verbose_name# 表头用

        context['posts'] = Post.objects.all()

        # 看一下是不是按标签在搜索的
        tag_slug = self.kwargs.get('tag_slug', None)
        if tag_slug:
            print("tag_slug:", tag_slug)
            # 从MyTag对应的数据库表里查询tag
            tag = get_object_or_404(MyTagForPost, slug=tag_slug)
            context['posts'] = context['posts'].filter(tags__in=[tag])

        # 看一下是不是get方式query数据
        submit_query_get = self.request.GET.get('submit_query_get', False)
        if submit_query_get:
            print('submit_query_get:', submit_query_get)

        # 快速搜索
        search_by_post_title_body = self.request.GET.get('search_by_post_title_body', False)
        if search_by_post_title_body:
            print("search_by_post_title_body:", search_by_post_title_body)
            context['posts'] = Post.objects.filter(
                Q(title__contains=search_by_post_title_body) |
                Q(body__contains=search_by_post_title_body)
            )


        #分页
        page = self.request.GET.get('page')
        paginator = Paginator(context['posts'], 10)  # 每页显示3篇文章
        print("paginator.num_pages:",paginator.num_pages)
        try:
            context['posts_page'] = paginator.page(page)
        except PageNotAnInteger:
            # 如果page参数不是一个整数就返回第一页
            context['posts_page'] = paginator.page(1)
        except EmptyPage:
            # 如果页数超出总页数就返回最后一页
            context['posts_page'] = paginator.page(paginator.num_pages)
        pagination_data = self.get_pagination_data(paginator, context['posts_page'])
        context.update(pagination_data)
        context['pages_count'] = paginator.num_pages


        print("len(context['posts_page']:",len(context['posts_page']))

        #文章很多时，要多页显示，但是在修改非首页内容时，比如修改某个文章，这个文章在第3页，如果不记住页数，修改完成后只能重定向到固定页。为了能记住当前页，用了下面的方法。
        if self.request.GET.__contains__("page"):
            current_page = self.request.GET["page"]
            print("current_page", current_page)
            context['current_page'] = current_page
        else:
            context['current_page'] = 1

        return context

    def post(self, request):  # ***** this method required! ******
        self.object_list = self.get_queryset()
        if request.method == 'POST':
            print("POST!!!")
            # 跳转页面用的，跳转指定页面用的post方法。
            if request.POST.__contains__("page_jump"):
                print(request.POST.get("page_jump"))
                return HttpResponse(request.POST.get("page_jump"))


class PostDetailView(DetailView):
    model = Post
    template_name = "PostDetailView.html"
    context_object_name = "post"
    # pk_url_kwarg = "pk"  # pk_url_kwarg默认值就是pk，这里可以覆盖，但必须和url中的命名组参数名称一致

    def get(self, request,year, month, day, post, *args, **kwargs):
        post = get_object_or_404(Post, slug=post, status="published", publish__year=year, publish__month=month,
                                 publish__day=day)

        # 列出文章对应的所有活动的评论
        comments = post.comments.filter(active=True)
        new_comment = None
        comment_form = CommentForm()
        # 显示相近Tag的文章列表
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_tags = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_tags.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

        return render(request, 'blog/post/PostDetailView.html',
                      {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form,
                       'similar_posts': similar_posts})

    def post(self, request, year, month, day, post):  # ***** this method required! ******
        post = get_object_or_404(Post, slug=post, status="published", publish__year=year, publish__month=month,
                                 publish__day=day)
        if request.method == 'POST':
            print("POST!!!")
            #先判断一下是否有评论权限
            sub = request.user.username  # 想要访问资源的用户
            obj = "post_detail_comment"  # 将要被访问的资源
            act = "post"  # 用户对资源进行的操作
            print('sub,obj,act:', sub, obj, act)
            if enforcer.enforce(sub, obj, act):
                pass
                print("权限通过！")
                comment_form = CommentForm(data=request.POST)
                if comment_form.is_valid():
                    # 通过表单直接创建新数据对象，但是不要保存到数据库中
                    new_comment = comment_form.save(commit=False)
                    new_comment.active = False
                    # 设置外键为当前文章
                    new_comment.post = post
                    # 将评论数据对象写入数据库
                    new_comment.save()
                    # return HttpResponse("ok")

                    # 列出文章对应的所有活动的评论
                    comments = post.comments.filter(active=True)
                    new_comment = None
                    post_tags_ids = post.tags.values_list('id', flat=True)
                    similar_tags = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
                    similar_posts = similar_tags.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[
                                    :4]
                    return render(request, 'blog/post/PostDetailView.html',
                                  {'post': post, 'comments': comments, 'new_comment': new_comment,
                                   'comment_form': comment_form,
                                   'similar_posts': similar_posts})
            else:
                return HttpResponse("您暂无评论权限，请联系管理员开通权限！")


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status="published", publish__year=year, publish__month=month,
                             publish__day=day)

    # 列出文章对应的所有活动的评论
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # 通过表单直接创建新数据对象，但是不要保存到数据库中
            new_comment = comment_form.save(commit=False)
            # 设置外键为当前文章
            new_comment.post = post
            # 将评论数据对象写入数据库
            new_comment.save()
    else:
        comment_form = CommentForm()

    # 显示相近Tag的文章列表
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_tags = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_tags.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post,'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form,'similar_posts': similar_posts})


def post_share(request, post_id):
    # 通过id 获取 post 对象
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == "POST":
        # 表单被提交
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # 验证表单数据
            cd = form.cleaned_data
            # 发送邮件......
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'chen320821@163.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # results = Post.objects.annotate(search=SearchVector('title', 'slug', 'body'), ).filter(search=query)

            # search_vector = SearchVector('title', 'body')

            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            # results = Post.objects.annotate(search=search_vector,rank=SearchRank(search_vector, search_query)).filter(search=search_query).order_by('-rank')

            results = Post.objects.annotate(search=search_vector,rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
            # 在上边的代码中，给title和body字段的搜索向量赋予了不同的权重。默认的权重D，C，B，A分别对应 0.1, 0.2, 0.4和1。
            # 我们给title字段的搜索向量赋予权重1.0，给body字段的搜索向量的权重是0.4，说明文章标题的重要性要比正文更重要，
            # 最后设置了只显示综合权重大于0.3的搜索结果。


            print('query:',query,"results:",results)
    return render(request, 'blog/post/search.html', {'query': query, "form": form, 'results': results})
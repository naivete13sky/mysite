from django.contrib import admin
from .models import Post, Comment
from django.utils.translation import gettext_lazy as _

# admin.site.register(Post)


# 更改管理后台名称
admin.site.site_header = '博客管理系统'
admin.site.site_title = '博客管理系统'


#为了实现在admin后台可页面上设置每页显示条数，通过下面方法，要创建一个过滤器PageSizeFilter。
#还要创建一个CustomModelAdmin类，这个类实现changelist_view方法。因为在过滤器PageSizeFilter无法重写changelist_view，所以要写此类实现类似效果。
class PageSizeFilter(admin.SimpleListFilter):
    title = _('每页显示条数')  # 在过滤器下拉列表中显示的标题

    parameter_name = 'page_size'  # URL参数名称

    def lookups(self, request, model_admin):
        # 返回一个包含元组的列表，每个元组包含两个值：
        # - 过滤器值，将作为URL参数值传递
        # - 在过滤器下拉列表中显示的文本
        return (
            ('10', _('10')),
            ('20', _('20')),
            ('50', _('50')),
            ('100', _('100')),
        )

    def queryset(self, request, queryset):
        pass
        return queryset

class CustomModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        if 'page_size' in request.GET:
            # 获取用户选择的每页显示条数
            page_size = int(request.GET['page_size'])
            # 将每页显示条数存储到session中
            request.session['page_size'] = page_size
        else:
            # 如果用户没有选择任何值，则从session中获取上次选择的值
            page_size = request.session.get('page_size', 10)

        # 设置每页显示条数
        self.list_per_page = page_size

        return super().changelist_view(request, extra_context)





@admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
class PostAdmin(CustomModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status', 'tag_list')
    list_filter = ('tags', 'status', 'created', 'publish', 'author', PageSizeFilter)
    search_fields = ('title', 'body',)
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish',)
    list_per_page = 20  # 设置每页显示的行数为 20

    def tag_list(self, obj):
        return ",".join(o.name for o in obj.tags.all())


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'body', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
    list_per_page = 20  # 设置每页显示的行数为 20
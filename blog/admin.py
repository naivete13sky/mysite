from django.contrib import admin
from .models import Post, Comment

# admin.site.register(Post)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status', 'tag_list')
    list_filter = ('status', 'created', 'publish', 'author',)
    search_fields = ('title', 'body',)
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish',)
    list_per_page = 2  # 设置每页显示的行数为 2

    def tag_list(self, obj):
        return ",".join(o.name for o in obj.tags.all())


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
    list_per_page = 2  # 设置每页显示的行数为 2
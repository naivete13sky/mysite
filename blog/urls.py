from django.urls import path
from . import views
from .feeds import LatestPostsFeed


app_name = 'blog'
urlpatterns = [
    # post views
    # path('', views.post_list, name='post_list'),
    path('',views.PostListView.as_view(),name='PostListView'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',views.PostDetailView.as_view(),name='PostDetailView'),
    # path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    # path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    # path('tag/<str:tag_slug>/',  views.post_list, name='post_list_by_tag'), # 这里的参数类型不要写slug，否则又会忽视中文，写str就行了
    path('tag/<str:tag_slug>/',  views.PostListView.as_view(), name='post_list_by_tag'), # 这里的参数类型不要写slug，否则又会忽视中文，写str就行了
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
]

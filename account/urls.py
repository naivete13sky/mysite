from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    # path('login/',auth_views.LoginView.as_view(),name='login'),
    # path('logout/',auth_views.LogoutView.as_view(),name='logout'),

    path('', views.dashboard, name='dashboard'),

    # # 修改密码
    # # 视图会控制渲染修改密码的页面和表单
    # path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    # # 视图在成功修改密码之后显示成功消息
    # path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    #
    # # 重置密码
    # # 重置，用户选择重置密码功能执行的视图，生成一个一次性重置密码链接和对应的验证token，然后发送邮件给用户。只能发给注册账户中指定的邮箱。
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # # 通知用户已经发送给了他们一封邮件重置密码
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # # 用户设置新密码的页面和功能控制
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # # 成功重置密码后执行的视图
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # 在第一个项目中，我们提到为应用配置单独的二级路由，有助于应用的复用。现在的account应用的urls.py文件中所有配置到内置视图的URL，可以用如下一行来代替：
    path('', include('django.contrib.auth.urls')),



    path('register/', views.register, name='register'),

    path('edit/', views.edit, name='edit'),

]
from django.shortcuts import render, HttpResponse
from django.contrib.auth import authenticate, login
from .forms import LoginForm,UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages


#做个试验，后面不用这个了
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse("Authenticated successfully")
                else:
                    return HttpResponse("Disabled account")
            else:
                return HttpResponse("Invalid login")

    else:
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})



#为用户制作一个登录成功后自己的首页
# 定义了一个参数section，可以用来追踪用户当前所在的功能板块。
# 使用@login_required装饰器，表示被装饰的视图只有在用户登录的情况下才会被执行
# 如果用户未登录，则会将用户重定向至Get请求附加的next参数指定的URL。这样设置之后，如果用户在未登录的情况下，无法看到首页。
@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})




def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # 建立新数据对象但是不写入数据库
            new_user = user_form.save(commit=False)
            # 设置密码,用了set_password()方法设置加密后的密码
            new_user.set_password(user_form.cleaned_data['password'])
            # 保存User对象
            new_user.save()

            # 当用户注册的时候，会自动建立一个空白的用户信息关联到用户。
            Profile.objects.create(user=new_user)

            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})



# 还必须让用户可以编辑他们的信息
# instance用于指定表单类实例化为某个具体的数据对象。
# 在这个例子里，将UserEditForminstance指定为request.user表示该对象是数据库中当前登录用户那一行的数据对象，而不是一个空白的数据对象，
# ProfileEditForm的instance属性指定为当前用户对应的Profile类中的那行数据。
# 这里如果不指定instance参数，则变成向数据库中增加两条新记录，而不是修改原有记录。
@login_required
def edit(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            #为视图增加了两条语句，分别在成功登录之后显示成功信息，在表单验证失败的时候显示错误信息。
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, "Error updating your profile")
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})
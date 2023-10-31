from django.db import models
from django.conf import settings

# Django内置验证模块的User模型只有非常基础的字段信息，可能需要额外的用户信息。最好的方式是建立一个用户信息模型，然后通过一对一关联字段，将用户信息模型和用户模型联系起来。
# 为了保持代码通用性，使用get_user_model()方法来获取用户模型；当定义其他表与内置User模型的关系时使用settings.AUTH_USER_MODEL指代User模型。
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='user/%Y/%m/%d/', blank=True)

    def __str__(self):
        return "Profile for user {}".format(self.user.username)
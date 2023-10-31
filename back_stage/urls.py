from django.urls import path
from . import views

app_name = 'back_stage'
urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index2'),



]
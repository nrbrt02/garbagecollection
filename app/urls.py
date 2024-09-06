from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('forbiden', views.forbidenpage, name="403"),


    path('adminn/', views.adminhome, name="admin-home"),
    
    
    path('money-collector/', views.mcollectorhome, name="money-collector-home"),
    
    
    path('login/', views.loginuser, name="login"),
    path('logout/', views.logoutuser, name="logoutuser"),
    path('adminn/empty', views.empty, name="admin-empty"),

]
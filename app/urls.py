from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('forbiden', views.forbidenpage, name="403"),


    path('adminn/', views.adminhome, name="admin-home"),
    path('locations/', views.locations, name="locations"),
    path('locations/load-sectors/', views.load_sectors, name="load_sectors"),
    path('locations/load-cells/', views.load_cells, name="load_cells"),
    path('locations/load-villages/', views.load_villages, name="load_villages"),

    path('change-status/<int:pk>', views.editResidence, name="edit-residence"),

    path('residence/', views.residence, name="residence"),
    path('residence/<int:pk>', views.editResidence, name="edit-residence"),
    path('residence/status/<int:pk>', views.changeResidence, name="change-residence"),

    path('clients/', views.clients, name="clients"),
    path('schedule/', views.schedule, name="schedule"),
    path('collection/', views.collection, name="collection"),
    path('overflow/', views.overflow, name="overflow"),

    path('feedbacks/', views.feedbacks, name="feedbacks"),
    path('feedbacks/unpost/<int:pk>', views.unpostfeedbacks, name="unpost-feedback"),
    path('feedbacks/post/<int:pk>', views.postfeedbacks, name="post-feedbacks"),
    
    
    path('money-collector/', views.mcollectorhome, name="money-collector-home"),
    
    
    path('login/', views.loginuser, name="login"),
    path('logout/', views.logoutuser, name="logoutuser"),
    path('adminn/empty', views.empty, name="admin-empty"),

]
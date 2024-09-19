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
    path('residence/edit/<int:pk>', views.editResidence, name="edit-residence"),
    path('residence/status/<int:pk>', views.changeResidence, name="change-residence"),

    path('clients/', views.clients, name="clients"),
    path('clients/edit/<int:pk>', views.editClient, name="edit-client"),
    path('clients/search/<str:email>', views.searchClient, name="search-client"),
    path('clients/status/<int:pk>', views.changeClient, name="change-clients"),

    path('schedule/', views.schedule, name="schedule"),
    path('schedule/edit/<int:pk>', views.editSchedule, name="edit-schedule"),
    path('schedule/status/<int:pk>', views.changeSchedule, name="change-schedule"),

    path('collection/', views.collection, name="collection"),
    path('collection/status/<int:pk>', views.changeCollection, name="change-collection"),
    path('collection/load-schedule/', views.load_schedule, name="load_schedule"),

    path('overflow/', views.overflow, name="overflow"),
    path('overflow/status/<int:pk>', views.statusOverflow, name="status-overflow"),

    path('feedbacks/', views.feedbacks, name="feedbacks"),
    path('feedbacks/status/<int:pk>', views.statusfeedbacks, name="status-feedback"),
    
    path('accounts/', views.accounts, name="accounts"),
    path('accounts/edit/<int:pk>', views.editAccounts, name="edit-accounts"),

    path('invoice/print/<int:pk>', views.invoice, name="invoice"),
    

    path('money-collector/', views.mcollectorhome, name="money-collector-home"),
    
    
    path('login/', views.loginuser, name="login"),
    path('logout/', views.logoutuser, name="logoutuser"),
    # path('adminn/empty', views.empty, name="admin-empty"),

]
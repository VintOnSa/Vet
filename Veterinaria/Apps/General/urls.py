from django.contrib import admin
from django.urls import path
from Apps.General import views

urlpatterns = [
    path('', views.Inicio, name="Inicio"),

]

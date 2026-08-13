from django.contrib import admin
from django.urls import path
from Apps.General import views

urlpatterns = [
    path('', views.Inicio, name="Inicio"),
    path('logout/', views.logout_view, name="Logout"),

#================================ FETCHS ============================================
    path('gPets/', views.gPets, name="ObtenerMascotas"),
    path('gAppointments/', views.gAppointments, name="ObtenerControles"),
    path('gOwner/', views.gOwner, name="ObtenerDuenos"),
    path('gVets/', views.gVets, name="ObtenerVeterinarios"),


#========================= FUNCIONES CONTROLES ======================================
    path('aControl/', views.aControl, name="AgendarControl"),

]

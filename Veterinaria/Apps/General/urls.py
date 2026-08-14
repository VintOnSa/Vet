from django.contrib import admin
from django.urls import path
from Apps.General import views

urlpatterns = [
    path('', views.Inicio, name="Inicio"),
    path('logout/', views.logout_view, name="Logout"),

#================================ FETCHS ============================================
    path('gPacientes/', views.gPatients, name="ObtenerMascotas"),
    path('gAgenda/', views.gAppointments, name="ObtenerControles"),
    path('gOwner/', views.gOwner, name="ObtenerDuenos"),
    path('gVeterinarios/', views.gVets, name="ObtenerVeterinarios"),
    path('gVacunas/', views.gVaccines, name="ObtenerVacunas"),


#========================= FUNCIONES CONTROLES ======================================
    path('aControl/', views.aControl, name="AgendarControl"),

]

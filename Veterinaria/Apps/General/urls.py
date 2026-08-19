from django.contrib import admin
from django.urls import path
from Apps.General import views

urlpatterns = [
    path('', views.Inicio, name="Inicio"),
    path('login/', views.login_view, name="Login"),
    path('login', views.login_view),
    path('logout/', views.logout_view, name="Logout"),

#================================ FETCHS ============================================
    path('gPacientes/', views.gPatients, name="ObtenerMascotas"),
    path('gAgenda/', views.gAppointments, name="ObtenerControles"),
    path('gOwner/', views.gOwner, name="ObtenerDuenos"),
    path('gVeterinarios/', views.gVets, name="ObtenerVeterinarios"),
    path('gVacunas/', views.gVaccines, name="ObtenerVacunas"),
    path('gProcedimientos/', views.gProcedures, name="ObtenerProcedimientos"),
    path('gDatosDash/', views.gDatosDash, name="ObtenerDatosDashboard"),
    path('gBodegas/', views.gBodegas, name="ObtenerBodegas"),
    path('gBodegaInsumos/<int:bodega_id>/', views.gBodegaInsumos, name="ObtenerInsumosBodega"),
    path('gInventario/', views.gInventario, name="ObtenerInventario"),
    path('gEspecies/', views.gEspecies, name="ObtenerEspecies"),
    path('gRazas/', views.gRazas, name="ObtenerRazas"),
    path('gPersonal/', views.gPersonal, name="ObtenerPersonal"),


#========================= FUNCIONES CONTROLES ======================================
    path('aControl/', views.aControl, name="AgendarControl"),
    path('eControl/', views.eControl, name="EditarControl"),
    path('cControl/', views.cControl, name="CancelarControl"),
    path('aDueno/', views.aDueno, name="AgregarDueno"),
    path('eUsuario/', views.eUsuario, name="EditarUsuario"),
    path('aPaciente/', views.aPaciente, name="AgregarPaciente"),
    path('ePaciente/', views.ePaciente, name="EditarPaciente"),
    path('aVacunaPaciente/', views.aVacunaPaciente, name="AgregarVacunaPaciente"),
    path('aCirugiaPaciente/', views.aCirugiaPaciente, name="AgregarCirugiaPaciente"),

#========================= CRUD ADMINISTRACION ======================================
    path('aBodega/', views.aBodega, name="AgregarBodega"),
    path('eBodega/', views.eBodega, name="EditarBodega"),
    path('delBodega/', views.delBodega, name="EliminarBodega"),
    path('aInsumo/', views.aInsumo, name="AgregarInsumo"),
    path('eInsumo/', views.eInsumo, name="EditarInsumo"),
    path('delInsumo/', views.delInsumo, name="EliminarInsumo"),
    path('aProcedimiento/', views.aProcedimiento, name="AgregarProcedimiento"),
    path('eProcedimiento/', views.eProcedimiento, name="EditarProcedimiento"),
    path('delProcedimiento/', views.delProcedimiento, name="EliminarProcedimiento"),
    path('aEspecie/', views.aEspecie, name="AgregarEspecie"),
    path('eEspecie/', views.eEspecie, name="EditarEspecie"),
    path('delEspecie/', views.delEspecie, name="EliminarEspecie"),
    path('aRaza/', views.aRaza, name="AgregarRaza"),
    path('eRaza/', views.eRaza, name="EditarRaza"),
    path('delRaza/', views.delRaza, name="EliminarRaza"),
    path('aPersonal/', views.aPersonal, name="AgregarPersonal"),
    path('ePersonal/', views.ePersonal, name="EditarPersonal"),
    path('delPersonal/', views.delPersonal, name="EliminarPersonal"),
    path('reset-password/', views.resetPassword, name="ResetPassword"),

    path('insertar', views.InsertarDatos, name="InsertarDatos"),

]

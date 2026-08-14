import json
from django.shortcuts import render, redirect
from Apps.General.models import *
from django.http import JsonResponse
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache

# Create your views here.
HORAS = ['10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30','14:00','14:30']


@never_cache
def logout_view(request):
    
    cache.clear()
    response = redirect('/')
    
    logout(request)
    request.session.flush()

    return response


def Inicio(request):
    user = request.user
    perfil = {}
    try:
        p = Personal.objects.get(correo = user.email)
        perfil = {
            'name': p.nombre,
            'rut': p.rut,
            'mail': p.correo,
            'phone': p.telefono,
            'type': p.profesion
        }
    except Personal.DoesNotExist:
        print("Usuario no Existe")
    except Exception as e:
        print(f"Error al Obtener Datos - Error: {e}")
        perfil = {}
        
    context = {
        'Horas': HORAS,
        'User': perfil
    }
    return render(request, "index.html", context)


def gVets(request):
    if request.method == "GET":
        try:
            v = Personal.objects.filter(profesion__icontains=['Veterinari']).exclude(activo="No")
            vets = []
            for vet in v:
                vet_data = {
                    'id': vet.pk,
                    'nombre': vet.nombre,
                    'rut': vet.rut,
                    'correo': vet.correo,
                    'direccion': vet.direccion,
                    'telefono': vet.telefono,
                    'cargo': vet.cargo,
                }
                vets.append(vet_data)

            data = {
                'veterinarios': vets
            }

            return JsonResponse(data)
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    else:
        return JsonResponse({'error': 'Sin autorizacion'}, status=401)

def gOwner(request):
    if request.method == "GET":
        try:
            o = Dueno.objects.all()
            owners = []
            for owner in o:
                owner_data = {
                    'name': owner.nombre,
                    'rut': owner.rut,
                    'address': owner.direccion,
                    'phone': owner.telefono,
                }
                owners.append(owner_data)

            data = {
                'duenos': owners
            }

            return JsonResponse(data)
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    else:
        return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def gPatients(request):
    if request.method == "GET":
        try:
            p = Paciente.objects.prefetch_related('dueno', 'vacunas')
            pets = []
            for pet in p:
                agendas = Agenda.objects.prefetch_related('paciente', 'id_vet').filter(paciente=pet)
                vacunas = pet.vacunas.all()
                pet_data = {
                    'id': pet.pk,
                    'nchip': str(pet.nchip),
                    'nombre': pet.nombre,
                    'especie': pet.especie,
                    'raza': pet.raza,
                    'genero':pet.genero,
                    'edad': pet.edad,
                    'meses': pet.meses,
                    'peso': pet.peso,
                    'marca': pet.marca,
                    'estd_rep': pet.estd_rep,
                    'paricion': pet.paricion,
                    'datos': pet.datos,
                    'fecha_ins': pet.fecha_ins.strftime(str("%d-%m-%Y")),
                    'dueno': {
                        'nombre': pet.dueno.nombre,
                        'rut': pet.dueno.rut
                    },
                    'vacunas': [
                        {   
                            'id': vac.vacuna.pk,
                            'codigo': vac.vacuna.codigo,
                            'vacuna': vac.nombre
                        } 
                        for vac in vacunas
                    ],
                    'controls' : [
                        { 
                            'id': str(c.pk),
                            'date': c.fecha.strftime("%d/%m/%Y"), 
                            'weight': c.peso, 
                            'age': c.edad, 
                            'diagnosis': c.diagnostico, 
                            'observations': c.observaciones,
                            'vet': c.veterinario
                        }
                        for c in agendas
                    ] 
                }
                pets.append(pet_data)

            data = {
                'pacientes' : pets
            }
            
            return JsonResponse(data)    
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    else:
        return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def gAppointments(request):
    if request.method == "GET":
        try:
            c = Agenda.objects.prefetch_related('paciente', 'id_vet')
            agendas = []
            for agenda in c:
                agenda_data = {

                    'id': str(agenda.pk),
                    'paciente': agenda.paciente.pk,
                    'procedimiento': agenda.procedimiento,
                    'datos_ing': agenda.datos_ing,
                    'fecha': agenda.fecha,
                    'hora': agenda.hora.strftime("%H:%M"),
                    'costo': agenda.costo,
                    'id_vet': agenda.id_vet.pk,
                    'veterinario': agenda.veterinario,
                    'estado': agenda.estado,
                    'peso': agenda.peso,
                    'edad': agenda.edad,
                    'meses': agenda.meses,
                    'temperatura': agenda.temperatura,
                    'diagnostico': agenda.diagnostico,
                    'observaciones': agenda.observaciones
                }

                agendas.append(agenda_data)

            data = {
                'agendas' : agendas 
            }
            
            return JsonResponse(data)    
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    else:
        return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def gVaccines(request):
    if request.method == "GET":
        try:
            v = Insumo.objects.filter(tipo='vacuna')
            vacunas = []
            for vacuna in v:
                vac_data = {
                    'id': vacuna.pk,
                    'codigo': vacuna.codigo,
                    'nombre': vacuna.nombre
                }
                vacunas.append(vac_data)
            data = {
                'vacunas': vacunas
            }
            return JsonResponse(data)
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    else:
        return JsonResponse({'error': 'Sin autorizacion'}, status=401)

#===================================================================================================================================================

def aControl(request):
    if request.method == "POST":
        data = {}
        try:
            paciente = Paciente.objects.get(pk=int(request.POST.get('paciente')))
            datos_ing = request.POST.get('datos_ing')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            vet = Personal.objects.get(pk=int(request.POST.get('id_vet')))

            with transaction.atomic():
                Agenda.objects.create(
                    paciente = paciente,
                    datos_ing = datos_ing,
                    fecha = fecha,
                    hora = hora,
                    veterinario = vet.nombre,
                    id_vet = vet
                )
                data = {
                    'success': True
                }

        except Exception as e:
            print(f"Error al guardar datos de Agenda - Error: {e}")
            data = {
                'success': False,
                'error': f"Error al registrar registro - Error: {e}"
            }
    return JsonResponse(data)



           




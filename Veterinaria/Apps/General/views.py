import json
from django.shortcuts import render, redirect
from Apps.General.models import *
from django.http import JsonResponse
from django.core.cache import cache
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
        p = Veterinario.objects.get(correo = user.email)
        perfil = {
            'name': p.nombre,
            'rut': p.rut,
            'mail': p.correo,
            'phone': p.telefono,
            'type': "Veterinario" if p else "Administracion"
        }
    except Veterinario.DoesNotExist:
        print("Veterinario no Existe")
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
            v = Veterinario.objects.all()
            vets = []
            for vet in v:
                vet_data = {
                    'id': vet.pk,
                    'name': vet.nombre,
                    'rut': vet.rut,
                    'mail': vet.correo,
                    'address': vet.direccion,
                    'phone': vet.telefono,
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


def gPets(request):
    if request.method == "GET":
        try:
            p = Paciente.objects.prefetch_related('dueno')
            pets = []
            for pet in p:
                controles = Control.objects.filter(mascota=pet)
                pet_data = {
                    'id': pet.pk,
                    'chip': str(pet.nchip),
                    'name': pet.nombre,
                    'species': pet.especie,
                    'breed': pet.raza,
                    'age': pet.edad,
                    'weight': pet.peso,
                    'owner': pet.dueno.nombre,
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
                        for c in controles
                    ] 
                }
                pets.append(pet_data)

            data = {
                'mascotas' : pets
            }
            print(data)
            
            return JsonResponse(data)    
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    else:
        return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def gAppointments(request):
    if request.method == "GET":
        try:
            c = Control.objects.prefetch_related('mascota')
            controles = []
            for control in c:
                control_data = {

                    'id': str(control.pk),
                    'petId': control.mascota.pk,
                    'date': control.fecha.strftime("%d/%m/%Y"),
                    'time': control.hora.strftime("%H:%M"),
                    'vet': control.veterinario,
                    'status': control.estado
                }

                controles.append(control_data)

            data = {
                'controles' : controles 
            }
            print(data)
            
            return JsonResponse(data)    
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    else:
        return JsonResponse({'error': 'Sin autorizacion'}, status=401)



#===================================================================================================================================================

def aControl(request):
    if request.method == "POST":
        data = {
            'message': 'No paso'
        }
        try:
            mas = request.POST.get('mascota_id')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            vet = request.POST.get('id_vet')

            print(mas,fecha,hora,vet)
            data = {
                'mensaje': 'Paso'
            }
        except Exception as e:
            print(f"Error al Guardar el Control - Error: {e}")
    return JsonResponse(data)



           




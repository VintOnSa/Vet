import json
import re
import unicodedata
from django.shortcuts import render, redirect
from Apps.General.models import *
from django.http import JsonResponse
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.utils import timezone

# Create your views here.
HORAS = ['10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30','14:00','14:30']
ESTADOS_ATENDIDA = ['Atendida', 'Realizada']


def es_admin(request):
    u = request.user
    return bool(u.is_authenticated and (u.is_staff or u.is_superuser))


def sin_permiso():
    return JsonResponse({'success': False, 'error': 'Solo administración puede realizar esta acción.'})


def _slugify_ascii(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()


def _generar_username(nombre_completo):
    partes = (nombre_completo or '').strip().split()
    primer_nombre = _slugify_ascii(partes[0]) if partes else 'usuario'
    apellido = _slugify_ascii(' '.join(partes[1:])) if len(partes) > 1 else ''

    if apellido:
        max_prefijo = len(primer_nombre) if primer_nombre else 1
        for n in range(1, max_prefijo + 1):
            candidato = primer_nombre[:n] + apellido
            if candidato and not User.objects.filter(username=candidato).exists():
                return candidato
        base = primer_nombre + apellido
    else:
        base = primer_nombre or 'usuario'
        if base and not User.objects.filter(username=base).exists():
            return base

    i = 1
    while User.objects.filter(username=f"{base}{i}").exists():
        i += 1
    return f"{base}{i}"


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
            'id': p.pk,
            'name': p.nombre,
            'rut': p.rut,
            'mail': p.correo,
            'phone': p.telefono,
            'direccion': p.direccion,
            'type': p.cargo
        }
    except Personal.DoesNotExist:
        print("Usuario no Existe")
    except Exception as e:
        print(f"Error al Obtener Datos - Error: {e}")
        perfil = {}

    es_admin = bool(user.is_authenticated and (user.is_staff or user.is_superuser))
    cargo_texto = (perfil.get('type') or '').lower()

    if es_admin:
        role = 'admin'
    elif 'secretar' in cargo_texto:
        role = 'secretaria'
    elif cargo_texto:
        role = 'staff'
    else:
        role = 'sin_asignar'

    perfil['is_admin'] = es_admin
    perfil['role'] = role

    context = {
        'Horas': HORAS,
        'User': perfil
    }
    return render(request, "index.html", context)


def gVets(request):
    if request.method == "GET":
        try:
            v = Personal.objects.filter(cargo__icontains='Veterinari').exclude(activo="No")
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
                    'id': owner.pk,
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
            p = Paciente.objects.prefetch_related('dueno', 'vacunas', 'cirugias')
            pets = []
            for pet in p:
                agendas = Agenda.objects.prefetch_related('paciente', 'id_vet').filter(paciente=pet)
                vacunas = pet.vacunas.all()
                cirugias = pet.cirugias.all()
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
                    'fecha_ins': pet.fecha_ins.strftime("%d-%m-%Y") if pet.fecha_ins else None,
                    'dueno': {
                        'id': pet.dueno.pk,
                        'nombre': pet.dueno.nombre,
                        'rut': pet.dueno.rut
                    },
                    'vacunas': [
                        {
                            'id': vac.vacuna.pk,
                            'codigo': vac.vacuna.codigo,
                            'vacuna': vac.nombre,
                            'fecha': vac.fecha.strftime("%d-%m-%Y") if vac.fecha else None
                        }
                        for vac in vacunas
                    ],
                    'cirugias': [
                        {
                            'id': c.pk,
                            'procedimiento_id': c.procedimiento.pk,
                            'nombre': c.nombre,
                            'fecha': c.fecha.strftime("%d-%m-%Y") if c.fecha else None
                        }
                        for c in cirugias
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

def gProcedures(request):
    if request.method == "GET":
        try:
            pr = Procedimiento.objects.all()
            procedimientos = []
            for proc in pr:
                procedimientos.append({
                    'id': proc.pk,
                    'nombre': proc.nombre,
                    'precio': proc.precio
                })
            data = {
                'procedimientos': procedimientos
            }
            return JsonResponse(data)
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    else:
        return JsonResponse({'error': 'Sin autorizacion'}, status=401)

def gDatosDash(request):
    if request.method == "GET":
        try:
            hoy = timezone.localdate()
            citas_hoy_qs = Agenda.objects.filter(fecha=hoy)
            citas_hoy = citas_hoy_qs.count()
            citas_hoy_atendidas = citas_hoy_qs.filter(estado__in=ESTADOS_ATENDIDA).count()
            pendientes_hoy = citas_hoy_qs.filter(estado='Pendiente').count()
            proxima = citas_hoy_qs.filter(estado='Pendiente', hora__gte=timezone.localtime().time()).order_by('hora').first()

            pacientes_total = Paciente.objects.count()

            mes, anio = hoy.month, hoy.year
            controles_mes = Agenda.objects.filter(fecha__month=mes, fecha__year=anio).count()

            if mes == 1:
                mes_ant, anio_ant = 12, anio - 1
            else:
                mes_ant, anio_ant = mes - 1, anio
            controles_mes_anterior = Agenda.objects.filter(fecha__month=mes_ant, fecha__year=anio_ant).count()

            variacion = None
            if controles_mes_anterior > 0:
                variacion = round(((controles_mes - controles_mes_anterior) / controles_mes_anterior) * 100)

            data = {
                'citas_hoy': citas_hoy,
                'citas_hoy_atendidas': citas_hoy_atendidas,
                'pendientes_hoy': pendientes_hoy,
                'proxima_hora': proxima.hora.strftime('%H:%M') if proxima else None,
                'pacientes_total': pacientes_total,
                'controles_mes': controles_mes,
                'controles_mes_variacion': variacion,
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
            tipo = request.POST.get('tipo')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            vet = Personal.objects.get(pk=int(request.POST.get('id_vet')))

            procedimiento_id = request.POST.get('procedimiento')
            procedimiento_nombre = None
            costo = None
            if procedimiento_id:
                proc = Procedimiento.objects.get(pk=int(procedimiento_id))
                procedimiento_nombre = proc.nombre
                costo = proc.precio

            with transaction.atomic():
                Agenda.objects.create(
                    paciente = paciente,
                    datos_ing = datos_ing,
                    tipo = tipo,
                    procedimiento = procedimiento_nombre,
                    costo = costo,
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


def eControl(request):
    if request.method == "POST":
        data = {}
        try:
            agenda = Agenda.objects.get(pk=int(request.POST.get('id')))

            es_admin = bool(request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))
            if agenda.fecha and agenda.fecha < timezone.localdate() and not es_admin:
                return JsonResponse({
                    'success': False,
                    'error': 'Solo administración puede editar una atención pasada.'
                })

            peso = request.POST.get('peso')
            edad = request.POST.get('edad')
            meses = request.POST.get('meses')
            temperatura = request.POST.get('temperatura')
            diagnostico = request.POST.get('diagnostico')
            observaciones = request.POST.get('observaciones')

            with transaction.atomic():
                agenda.peso = peso
                agenda.edad = int(edad) if edad not in (None, '') else agenda.edad
                agenda.meses = int(meses) if meses not in (None, '') else agenda.meses
                agenda.temperatura = temperatura
                agenda.diagnostico = diagnostico
                agenda.observaciones = observaciones
                agenda.estado = 'Atendida'
                agenda.save()

                if agenda.paciente:
                    if peso not in (None, ''):
                        agenda.paciente.peso = peso
                    if edad not in (None, ''):
                        agenda.paciente.edad = int(edad)
                    if meses not in (None, ''):
                        agenda.paciente.meses = int(meses)
                    agenda.paciente.save()

            data = {
                'success': True
            }

        except Exception as e:
            print(f"Error al editar datos de Agenda - Error: {e}")
            data = {
                'success': False,
                'error': f"Error al editar registro - Error: {e}"
            }
    return JsonResponse(data)


def aDueno(request):
    if request.method == "POST":
        data = {}
        try:
            nombre = request.POST.get('nombre')
            rut = request.POST.get('rut')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')
            direccion = request.POST.get('direccion')

            with transaction.atomic():
                dueno = Dueno.objects.create(
                    nombre = nombre,
                    rut = rut,
                    correo = correo,
                    telefono = int(telefono) if telefono not in (None, '') else None,
                    direccion = direccion
                )
                data = {
                    'success': True,
                    'data': {
                        'id': dueno.pk,
                        'name': dueno.nombre,
                        'rut': dueno.rut,
                        'phone': dueno.telefono,
                        'address': dueno.direccion
                    }
                }

        except Exception as e:
            print(f"Error al guardar dueño - Error: {e}")
            data = {
                'success': False,
                'error': f"Error al registrar dueño - Error: {e}"
            }
    return JsonResponse(data)


def eUsuario(request):
    if request.method == "POST":
        data = {}
        try:
            personal = Personal.objects.get(correo=request.user.email)
            telefono = request.POST.get('telefono')

            with transaction.atomic():
                personal.nombre = request.POST.get('nombre')
                personal.rut = request.POST.get('rut')
                personal.correo = request.POST.get('correo')
                personal.telefono = int(telefono) if telefono not in (None, '') else None
                personal.direccion = request.POST.get('direccion')
                personal.save()

            data = {
                'success': True,
                'data': {
                    'name': personal.nombre,
                    'rut': personal.rut,
                    'mail': personal.correo,
                    'phone': personal.telefono,
                    'direccion': personal.direccion,
                    'type': personal.cargo
                }
            }

        except Personal.DoesNotExist:
            data = {
                'success': False,
                'error': 'No se encontró un perfil de personal asociado a este usuario.'
            }
        except Exception as e:
            print(f"Error al editar perfil - Error: {e}")
            data = {
                'success': False,
                'error': f"Error al editar perfil - Error: {e}"
            }
    return JsonResponse(data)


def aPaciente(request):
    if request.method == "POST":
        data = {}
        try:
            dueno = Dueno.objects.get(pk=int(request.POST.get('dueno')))
            edad = request.POST.get('edad')
            meses = request.POST.get('meses')
            nchip = request.POST.get('nchip')

            with transaction.atomic():
                paciente = Paciente.objects.create(
                    nchip = int(nchip) if nchip not in (None, '') else None,
                    nombre = request.POST.get('nombre'),
                    especie = request.POST.get('especie'),
                    raza = request.POST.get('raza'),
                    genero = request.POST.get('genero'),
                    edad = int(edad) if edad not in (None, '') else None,
                    meses = int(meses) if meses not in (None, '') else None,
                    peso = request.POST.get('peso'),
                    marca = request.POST.get('marca'),
                    estd_rep = request.POST.get('estd_rep'),
                    dueno = dueno,
                    fecha_ins = timezone.now()
                )

                vacunas_raw = request.POST.get('vacunas') or ''
                for vid in vacunas_raw.split(','):
                    vid = vid.strip()
                    if not vid:
                        continue
                    try:
                        insumo = Insumo.objects.get(pk=int(vid))
                        VacunasPaciente.objects.create(
                            paciente = paciente,
                            vacuna = insumo,
                            nombre = insumo.nombre
                        )
                    except Insumo.DoesNotExist:
                        continue

                data = {
                    'success': True,
                    'id': paciente.pk
                }

        except Exception as e:
            print(f"Error al guardar paciente - Error: {e}")
            data = {
                'success': False,
                'error': f"Error al registrar paciente - Error: {e}"
            }
    return JsonResponse(data)


def ePaciente(request):
    if request.method == "POST":
        data = {}
        try:
            paciente = Paciente.objects.get(pk=int(request.POST.get('id')))
            edad = request.POST.get('edad')
            meses = request.POST.get('meses')
            nchip = request.POST.get('nchip')
            dueno_id = request.POST.get('dueno')

            with transaction.atomic():
                paciente.nchip = int(nchip) if nchip not in (None, '') else None
                paciente.nombre = request.POST.get('nombre')
                paciente.especie = request.POST.get('especie')
                paciente.raza = request.POST.get('raza')
                paciente.genero = request.POST.get('genero')
                paciente.edad = int(edad) if edad not in (None, '') else None
                paciente.meses = int(meses) if meses not in (None, '') else None
                paciente.peso = request.POST.get('peso')
                paciente.marca = request.POST.get('marca')
                paciente.estd_rep = request.POST.get('estd_rep')
                if dueno_id:
                    paciente.dueno = Dueno.objects.get(pk=int(dueno_id))
                paciente.save()

            data = {
                'success': True,
                'id': paciente.pk
            }

        except Exception as e:
            print(f"Error al editar paciente - Error: {e}")
            data = {
                'success': False,
                'error': f"Error al editar paciente - Error: {e}"
            }
    return JsonResponse(data)


def aVacunaPaciente(request):
    if request.method == "POST":
        data = {}
        try:
            paciente = Paciente.objects.get(pk=int(request.POST.get('paciente')))
            vacuna = Insumo.objects.get(pk=int(request.POST.get('vacuna')))
            fecha = request.POST.get('fecha')

            with transaction.atomic():
                VacunasPaciente.objects.create(
                    paciente = paciente,
                    vacuna = vacuna,
                    nombre = vacuna.nombre,
                    fecha = fecha or None
                )

            data = {
                'success': True
            }

        except Exception as e:
            print(f"Error al registrar vacuna - Error: {e}")
            data = {
                'success': False,
                'error': f"Error al registrar vacuna - Error: {e}"
            }
    return JsonResponse(data)


def aCirugiaPaciente(request):
    if request.method == "POST":
        data = {}
        try:
            paciente = Paciente.objects.get(pk=int(request.POST.get('paciente')))
            procedimiento = Procedimiento.objects.get(pk=int(request.POST.get('procedimiento')))
            fecha = request.POST.get('fecha')

            with transaction.atomic():
                CirugiasPaciente.objects.create(
                    paciente = paciente,
                    procedimiento = procedimiento,
                    nombre = procedimiento.nombre,
                    fecha = fecha or None
                )

            data = {
                'success': True
            }

        except Exception as e:
            print(f"Error al registrar procedimiento - Error: {e}")
            data = {
                'success': False,
                'error': f"Error al registrar procedimiento - Error: {e}"
            }
    return JsonResponse(data)


#===================================================================================================================================================
# BODEGAS
#===================================================================================================================================================

def gBodegas(request):
    if request.method == "GET":
        try:
            bodegas = [
                {
                    'id': b.pk,
                    'codigo': b.codigo,
                    'nombre': b.nombre,
                    'ubicacion': b.ubicacion,
                    'encargado': b.encargado,
                    'insumos_count': b.insumo_set.count()
                }
                for b in Bodega.objects.all()
            ]
            return JsonResponse({'bodegas': bodegas})
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def gBodegaInsumos(request, bodega_id):
    if request.method == "GET":
        try:
            insumos = [
                {
                    'id': i.pk,
                    'codigo': i.codigo,
                    'nombre': i.nombre,
                    'tipo': i.tipo,
                    'unidad': i.unidad,
                    'stock': i.stock
                }
                for i in Insumo.objects.filter(ubicacion_id=bodega_id)
            ]
            return JsonResponse({'insumos': insumos})
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def aBodega(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            with transaction.atomic():
                bodega = Bodega.objects.create(
                    nombre = request.POST.get('nombre'),
                    ubicacion = request.POST.get('ubicacion'),
                    encargado = request.POST.get('encargado')
                )
                bodega.codigo = f"BOD-{bodega.pk:03d}"
                bodega.save()

            data = {
                'success': True,
                'data': {
                    'id': bodega.pk,
                    'codigo': bodega.codigo,
                    'nombre': bodega.nombre,
                    'ubicacion': bodega.ubicacion,
                    'encargado': bodega.encargado
                }
            }
        except Exception as e:
            print(f"Error al guardar bodega - Error: {e}")
            data = {'success': False, 'error': f"Error al registrar bodega - Error: {e}"}
    return JsonResponse(data)


def eBodega(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            bodega = Bodega.objects.get(pk=int(request.POST.get('id')))
            with transaction.atomic():
                bodega.nombre = request.POST.get('nombre')
                bodega.ubicacion = request.POST.get('ubicacion')
                bodega.encargado = request.POST.get('encargado')
                bodega.save()

            data = {
                'success': True,
                'data': {
                    'id': bodega.pk,
                    'codigo': bodega.codigo,
                    'nombre': bodega.nombre,
                    'ubicacion': bodega.ubicacion,
                    'encargado': bodega.encargado
                }
            }
        except Exception as e:
            print(f"Error al editar bodega - Error: {e}")
            data = {'success': False, 'error': f"Error al editar bodega - Error: {e}"}
    return JsonResponse(data)


def delBodega(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            bodega = Bodega.objects.get(pk=int(request.POST.get('id')))
            if Insumo.objects.filter(ubicacion=bodega).exists():
                return JsonResponse({'success': False, 'error': 'No se puede eliminar: hay insumos asignados a esta bodega.'})
            with transaction.atomic():
                bodega.delete()
            data = {'success': True}
        except Exception as e:
            print(f"Error al eliminar bodega - Error: {e}")
            data = {'success': False, 'error': f"Error al eliminar bodega - Error: {e}"}
    return JsonResponse(data)


#===================================================================================================================================================
# INSUMOS / VACUNAS (INVENTARIO)
#===================================================================================================================================================

def _siguiente_codigo_insumo(tipo):
    prefijo = 'VAC' if tipo == 'vacuna' else 'INS'
    existentes = Insumo.objects.filter(codigo__startswith=f"{prefijo}-")
    max_n = 0
    for it in existentes:
        m = re.search(r'(\d+)$', it.codigo or '')
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"{prefijo}-{str(max_n + 1).zfill(3)}"


def gInventario(request):
    if request.method == "GET":
        try:
            productos = []
            for i in Insumo.objects.select_related('ubicacion').all():
                productos.append({
                    'id': i.pk,
                    'codigo': i.codigo,
                    'nombre': i.nombre,
                    'tipo': i.tipo,
                    'unidad': i.unidad,
                    'stock': i.stock,
                    'precio': i.precio,
                    'descuento': i.descuento,
                    'ubicacion': i.ubicacion.pk if i.ubicacion else None,
                    'ubicacion_nombre': i.ubicacion.nombre if i.ubicacion else None
                })
            return JsonResponse({'productos': productos})
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def aInsumo(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            tipo = request.POST.get('tipo')
            stock = request.POST.get('stock')
            precio = request.POST.get('precio')
            descuento = request.POST.get('descuento')
            ubicacion_id = request.POST.get('ubicacion')
            bodega = Bodega.objects.get(pk=int(ubicacion_id)) if ubicacion_id else Bodega.objects.first()

            with transaction.atomic():
                insumo = Insumo.objects.create(
                    codigo = _siguiente_codigo_insumo(tipo),
                    nombre = request.POST.get('nombre'),
                    tipo = tipo,
                    unidad = request.POST.get('unidad'),
                    stock = int(stock) if stock not in (None, '') else None,
                    precio = int(precio) if precio not in (None, '') else None,
                    descuento = int(descuento) if descuento not in (None, '') else 0,
                    ubicacion = bodega
                )

            data = {
                'success': True,
                'data': {
                    'id': insumo.pk,
                    'codigo': insumo.codigo,
                    'nombre': insumo.nombre,
                    'tipo': insumo.tipo,
                    'unidad': insumo.unidad,
                    'stock': insumo.stock,
                    'precio': insumo.precio,
                    'descuento': insumo.descuento,
                    'ubicacion': insumo.ubicacion.pk,
                    'ubicacion_nombre': insumo.ubicacion.nombre
                }
            }
        except Exception as e:
            print(f"Error al guardar insumo - Error: {e}")
            data = {'success': False, 'error': f"Error al registrar insumo - Error: {e}"}
    return JsonResponse(data)


def eInsumo(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            insumo = Insumo.objects.get(pk=int(request.POST.get('id')))
            stock = request.POST.get('stock')
            precio = request.POST.get('precio')
            descuento = request.POST.get('descuento')
            ubicacion_id = request.POST.get('ubicacion')

            with transaction.atomic():
                insumo.nombre = request.POST.get('nombre')
                insumo.tipo = request.POST.get('tipo')
                insumo.unidad = request.POST.get('unidad')
                insumo.stock = int(stock) if stock not in (None, '') else None
                insumo.precio = int(precio) if precio not in (None, '') else None
                insumo.descuento = int(descuento) if descuento not in (None, '') else 0
                if ubicacion_id:
                    insumo.ubicacion = Bodega.objects.get(pk=int(ubicacion_id))
                insumo.save()

            data = {
                'success': True,
                'data': {
                    'id': insumo.pk,
                    'codigo': insumo.codigo,
                    'nombre': insumo.nombre,
                    'tipo': insumo.tipo,
                    'unidad': insumo.unidad,
                    'stock': insumo.stock,
                    'precio': insumo.precio,
                    'descuento': insumo.descuento,
                    'ubicacion': insumo.ubicacion.pk,
                    'ubicacion_nombre': insumo.ubicacion.nombre
                }
            }
        except Exception as e:
            print(f"Error al editar insumo - Error: {e}")
            data = {'success': False, 'error': f"Error al editar insumo - Error: {e}"}
    return JsonResponse(data)


def delInsumo(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            insumo = Insumo.objects.get(pk=int(request.POST.get('id')))
            with transaction.atomic():
                insumo.delete()
            data = {'success': True}
        except Exception as e:
            print(f"Error al eliminar insumo - Error: {e}")
            data = {'success': False, 'error': f"Error al eliminar insumo - Error: {e}"}
    return JsonResponse(data)


#===================================================================================================================================================
# PROCEDIMIENTOS
#===================================================================================================================================================

def aProcedimiento(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            precio = request.POST.get('precio')
            with transaction.atomic():
                proc = Procedimiento.objects.create(
                    nombre = request.POST.get('nombre'),
                    precio = int(precio) if precio not in (None, '') else None
                )
            data = {'success': True, 'data': {'id': proc.pk, 'nombre': proc.nombre, 'precio': proc.precio}}
        except Exception as e:
            print(f"Error al guardar procedimiento - Error: {e}")
            data = {'success': False, 'error': f"Error al registrar procedimiento - Error: {e}"}
    return JsonResponse(data)


def eProcedimiento(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            proc = Procedimiento.objects.get(pk=int(request.POST.get('id')))
            precio = request.POST.get('precio')
            with transaction.atomic():
                proc.nombre = request.POST.get('nombre')
                proc.precio = int(precio) if precio not in (None, '') else None
                proc.save()
            data = {'success': True, 'data': {'id': proc.pk, 'nombre': proc.nombre, 'precio': proc.precio}}
        except Exception as e:
            print(f"Error al editar procedimiento - Error: {e}")
            data = {'success': False, 'error': f"Error al editar procedimiento - Error: {e}"}
    return JsonResponse(data)


def delProcedimiento(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            proc = Procedimiento.objects.get(pk=int(request.POST.get('id')))
            with transaction.atomic():
                proc.delete()
            data = {'success': True}
        except Exception as e:
            print(f"Error al eliminar procedimiento - Error: {e}")
            data = {'success': False, 'error': f"Error al eliminar procedimiento - Error: {e}"}
    return JsonResponse(data)


#===================================================================================================================================================
# ESPECIES Y RAZAS
#===================================================================================================================================================

def gEspecies(request):
    if request.method == "GET":
        try:
            especies = [{'id': e.pk, 'nombre': e.nombre} for e in Especie.objects.all()]
            return JsonResponse({'especies': especies})
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def aEspecie(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            with transaction.atomic():
                especie = Especie.objects.create(nombre=request.POST.get('nombre'))
            data = {'success': True, 'data': {'id': especie.pk, 'nombre': especie.nombre}}
        except Exception as e:
            print(f"Error al guardar especie - Error: {e}")
            data = {'success': False, 'error': f"Error al registrar especie - Error: {e}"}
    return JsonResponse(data)


def eEspecie(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            especie = Especie.objects.get(pk=int(request.POST.get('id')))
            with transaction.atomic():
                especie.nombre = request.POST.get('nombre')
                especie.save()
            data = {'success': True, 'data': {'id': especie.pk, 'nombre': especie.nombre}}
        except Exception as e:
            print(f"Error al editar especie - Error: {e}")
            data = {'success': False, 'error': f"Error al editar especie - Error: {e}"}
    return JsonResponse(data)


def delEspecie(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            especie = Especie.objects.get(pk=int(request.POST.get('id')))
            with transaction.atomic():
                especie.delete()
            data = {'success': True}
        except Exception as e:
            print(f"Error al eliminar especie - Error: {e}")
            data = {'success': False, 'error': f"Error al eliminar especie - Error: {e}"}
    return JsonResponse(data)


def gRazas(request):
    if request.method == "GET":
        try:
            razas = [
                {'id': r.pk, 'nombre': r.nombre, 'especie_id': r.especie.pk}
                for r in Raza.objects.select_related('especie').all()
            ]
            return JsonResponse({'razas': razas})
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def aRaza(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            especie = Especie.objects.get(pk=int(request.POST.get('especie')))
            with transaction.atomic():
                raza = Raza.objects.create(especie=especie, nombre=request.POST.get('nombre'))
            data = {'success': True, 'data': {'id': raza.pk, 'nombre': raza.nombre, 'especie_id': especie.pk}}
        except Exception as e:
            print(f"Error al guardar raza - Error: {e}")
            data = {'success': False, 'error': f"Error al registrar raza - Error: {e}"}
    return JsonResponse(data)


def eRaza(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            raza = Raza.objects.get(pk=int(request.POST.get('id')))
            especie_id = request.POST.get('especie')
            with transaction.atomic():
                raza.nombre = request.POST.get('nombre')
                if especie_id:
                    raza.especie = Especie.objects.get(pk=int(especie_id))
                raza.save()
            data = {'success': True, 'data': {'id': raza.pk, 'nombre': raza.nombre, 'especie_id': raza.especie.pk}}
        except Exception as e:
            print(f"Error al editar raza - Error: {e}")
            data = {'success': False, 'error': f"Error al editar raza - Error: {e}"}
    return JsonResponse(data)


def delRaza(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            raza = Raza.objects.get(pk=int(request.POST.get('id')))
            with transaction.atomic():
                raza.delete()
            data = {'success': True}
        except Exception as e:
            print(f"Error al eliminar raza - Error: {e}")
            data = {'success': False, 'error': f"Error al eliminar raza - Error: {e}"}
    return JsonResponse(data)


#===================================================================================================================================================
# PERSONAL
#===================================================================================================================================================

def gPersonal(request):
    if request.method == "GET":
        if not es_admin(request):
            return JsonResponse({'error': 'Sin autorizacion'}, status=401)
        try:
            personal = [
                {
                    'id': p.pk,
                    'rut': p.rut,
                    'nombre': p.nombre,
                    'cargo': p.cargo,
                    'telefono': p.telefono,
                    'correo': p.correo,
                    'usuario': p.usuario,
                    'activo': p.activo
                }
                for p in Personal.objects.all()
            ]
            return JsonResponse({'personal': personal})
        except Exception as e:
            print(f"Error al Obtener Datos - Error: {e}")
            return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)
    return JsonResponse({'error': 'Sin autorizacion'}, status=401)


def aPersonal(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            telefono = request.POST.get('telefono')
            nombre = request.POST.get('nombre')
            correo = request.POST.get('correo')
            partes = (nombre or '').strip().split()

            cuenta_creada = False
            with transaction.atomic():
                username = _generar_username(nombre)
                personal = Personal.objects.create(
                    rut = request.POST.get('rut'),
                    nombre = nombre,
                    cargo = request.POST.get('cargo'),
                    telefono = int(telefono) if telefono not in (None, '') else None,
                    correo = correo,
                    usuario = username,
                    activo = request.POST.get('activo') or 'true'
                )

                if correo and not User.objects.filter(email=correo).exists():
                    User.objects.create_user(
                        username = username,
                        email = correo,
                        password = 'sanjoaquin',
                        first_name = partes[0] if partes else '',
                        last_name = ' '.join(partes[1:]) if len(partes) > 1 else ''
                    )
                    cuenta_creada = True

            mensaje = f"Personal registrado. Usuario: {username}." if cuenta_creada else "Personal registrado (ya existía una cuenta con ese correo)."
            data = {
                'success': True,
                'message': mensaje,
                'data': {
                    'id': personal.pk, 'rut': personal.rut, 'nombre': personal.nombre,
                    'cargo': personal.cargo, 'telefono': personal.telefono,
                    'correo': personal.correo, 'usuario': personal.usuario, 'activo': personal.activo
                }
            }
        except Exception as e:
            print(f"Error al guardar personal - Error: {e}")
            data = {'success': False, 'error': f"Error al registrar personal - Error: {e}"}
    return JsonResponse(data)


def ePersonal(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            personal = Personal.objects.get(pk=int(request.POST.get('id')))
            telefono = request.POST.get('telefono')
            with transaction.atomic():
                personal.rut = request.POST.get('rut')
                personal.nombre = request.POST.get('nombre')
                personal.cargo = request.POST.get('cargo')
                personal.telefono = int(telefono) if telefono not in (None, '') else None
                personal.correo = request.POST.get('correo')
                personal.usuario = request.POST.get('usuario')
                personal.activo = request.POST.get('activo') or 'true'
                personal.save()
            data = {
                'success': True,
                'data': {
                    'id': personal.pk, 'rut': personal.rut, 'nombre': personal.nombre,
                    'cargo': personal.cargo, 'telefono': personal.telefono,
                    'correo': personal.correo, 'usuario': personal.usuario, 'activo': personal.activo
                }
            }
        except Exception as e:
            print(f"Error al editar personal - Error: {e}")
            data = {'success': False, 'error': f"Error al editar personal - Error: {e}"}
    return JsonResponse(data)


def delPersonal(request):
    if request.method == "POST":
        if not es_admin(request):
            return sin_permiso()
        data = {}
        try:
            personal = Personal.objects.get(pk=int(request.POST.get('id')))
            with transaction.atomic():
                User.objects.filter(email=personal.correo).delete()
                personal.delete()
            data = {'success': True}
        except Exception as e:
            print(f"Error al eliminar personal - Error: {e}")
            data = {'success': False, 'error': f"Error al eliminar personal - Error: {e}"}
    return JsonResponse(data)


def resetPassword(request):
    if request.method == "POST":
        data = {}
        try:
            personal = Personal.objects.get(pk=int(request.POST.get('id')))

            es_propio = bool(request.user.is_authenticated and personal.correo == request.user.email)
            if not es_admin(request) and not es_propio:
                return sin_permiso()

            nueva_clave = request.POST.get('nueva_clave') or ''
            confirmar = request.POST.get('confirmar') or ''

            if len(nueva_clave) < 6:
                return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres.'})
            if nueva_clave != confirmar:
                return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden.'})

            usuario = User.objects.get(email=personal.correo)
            with transaction.atomic():
                usuario.set_password(nueva_clave)
                usuario.save()
            data = {'success': True, 'message': 'Contraseña actualizada correctamente.'}
        except Personal.DoesNotExist:
            data = {'success': False, 'error': 'No se encontró el registro de personal.'}
        except User.DoesNotExist:
            data = {'success': False, 'error': 'No existe una cuenta de acceso asociada a este correo.'}
        except Exception as e:
            print(f"Error al restablecer contraseña - Error: {e}")
            data = {'success': False, 'error': f"Error al restablecer contraseña - Error: {e}"}
    return JsonResponse(data)


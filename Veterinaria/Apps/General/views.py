import json
import re
import unicodedata
from django.shortcuts import render, redirect
from Apps.General.models import *
from django.contrib import messages
from django.http import JsonResponse
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import never_cache
from django.utils import timezone

# Create your views here.
HORAS = ['10:00','10:30','11:00','11:30','12:00','12:30','13:00','13:30','14:00','14:30']
ESTADOS_ATENDIDA = ['Atendida', 'Realizada']
LOGIN_URL = '/login'


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

    if len(partes) >= 4:
        apellido = _slugify_ascii(partes[2])
    elif len(partes) >= 2:
        apellido = _slugify_ascii(partes[1])
    else:
        apellido = ''

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


def check_activeuser(request, usuario, vista):
    try:
        user = Personal.objects.get(usuario=usuario)
        mensaje = ''
        
        if user.activo == "true":
            if vista == 'login':
                mensaje = f"Bienvenido {(User.objects.get(username=usuario)).first_name}"
            estado = True
        else:
            mensaje = 'Usuario Inactivo, contactar con Administrador'
            estado = False
        
        respuesta = {
            'mensaje': mensaje if mensaje else '',
            'estado': estado
        }
    except Personal.DoesNotExist:
        respuesta = {
            'mensaje': "Usuario no existe",
            'estado': False
        }
    return respuesta


def validar_rut_formato(value):
    return bool(re.fullmatch(r"[0-9]{7,8}-[0-9Kk]", value))

def validar_rut(rut: str) -> bool:
    # Limpiar espacios y pasar K a mayúscula
    rut = rut.strip().upper()

    # Validar formato: 7 u 8 dígitos + guión + dígito verificador
    import re

    if not re.fullmatch(r"[0-9]{7,8}-[0-9K]", rut):
        return False

    numero, dv = rut.split("-")

    # Calcular dígito verificador
    suma = 0
    multiplicador = 2

    for digito in reversed(numero):
        suma += int(digito) * multiplicador
        multiplicador += 1

        if multiplicador > 7:
            multiplicador = 2

    resto = suma % 11
    resultado = 11 - resto

    if resultado == 11:
        dv_calculado = "0"
    elif resultado == 10:
        dv_calculado = "K"
    else:
        dv_calculado = str(resultado)

    return dv == dv_calculado

#===================================================================================================================================================
# AUTENTICACIÓN
#===================================================================================================================================================

@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    error = None
    if request.method == "POST":
        usuario = request.POST.get('usuario')
        password = request.POST.get('password')
        user = authenticate(request, username=usuario, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:    
                return redirect('/')
            else:
                activo = check_activeuser(request, usuario, 'login')
                if activo['estado'] == True:
                    messages.success(request, activo['mensaje'])
                    return redirect('/')
                else: 
                    error = activo['mensaje']
                    logout(request)
                    request.session.flush()
        else:
            error = 'Usuario o contraseña incorrectos.'

    return render(request, 'login.html', {'error': error})


@never_cache
def logout_view(request):

    cache.clear()
    response = redirect('/login')

    logout(request)
    request.session.flush()

    return response


@login_required(login_url=LOGIN_URL)
@require_GET
def Inicio(request):
    user = request.user
    
    activo = check_activeuser(request, user.username, 'inicio')
    if user.is_staff:
        print(f"Estado: {activo['estado']}")
    else:
        if activo['estado'] == False:
            messages.error(request, activo['mensaje'])
            return redirect('/logout')
    
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

    es_admin_actual = bool(user.is_authenticated and (user.is_staff or user.is_superuser))
    cargo_texto = (perfil.get('type') or '').lower()

    if es_admin_actual:
        role = 'admin'
    elif 'secretar' in cargo_texto:
        role = 'secretaria'
    elif cargo_texto:
        role = 'staff'
    else:
        role = 'sin_asignar'

    perfil['is_admin'] = es_admin_actual
    perfil['role'] = role

    context = {
        'Horas': HORAS,
        'User': perfil
    }
    return render(request, "index.html", context)


#===================================================================================================================================================
# FETCHS (lectura general - requieren sesión iniciada)
#===================================================================================================================================================

@login_required(login_url=LOGIN_URL)
@require_GET
def gVets(request):
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


@login_required(login_url=LOGIN_URL)
@require_GET
def gOwner(request):
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


@login_required(login_url=LOGIN_URL)
@require_GET
def gPatients(request):
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


@login_required(login_url=LOGIN_URL)
@require_GET
def gAppointments(request):
    try:
        user = request.user
        if user:
            try:
                Agenda.marcar_expirados()
            except Exception as e:
                print(f"Error al Limpiar Agendas Pendientes - Error {e}")

            c = Agenda.objects.prefetch_related('paciente', 'id_vet')
        else:
            return JsonResponse({'error': 'Error al obtener los datos, Usuario no Existe'}, status=403)

        agendas = []
        for agenda in c:
            agenda_data = {

                'id': str(agenda.pk),
                'paciente': agenda.paciente.pk,
                'tipo': agenda.tipo,
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
                'observaciones': agenda.observaciones,
                'motivo': agenda.cancelado
            }

            agendas.append(agenda_data)

        data = {
            'agendas' : agendas
        }

        return JsonResponse(data)
    except Exception as e:
        print(f"Error al Obtener Datos - Error: {e}")
        return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)


@login_required(login_url=LOGIN_URL)
@require_GET
def gVaccines(request):
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


@login_required(login_url=LOGIN_URL)
@require_GET
def gProcedures(request):
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


@login_required(login_url=LOGIN_URL)
@require_GET
def gDatosDash(request):
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


#===================================================================================================================================================
# FUNCIONES CONTROLES / PACIENTES (requieren sesión iniciada)
#===================================================================================================================================================

@login_required(login_url=LOGIN_URL)
@require_POST
def aControl(request):
    data = {}
    try:
        paciente = Paciente.objects.get(pk=int(request.POST.get('paciente')))
        datos_ing = request.POST.get('datos_ing').capitalize()
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


@login_required(login_url=LOGIN_URL)
@require_POST
def eControl(request):
    data = {}
    try:
        agenda = Agenda.objects.get(pk=int(request.POST.get('id')))

        if agenda.fecha and agenda.fecha < timezone.localdate() and not es_admin(request):
            return JsonResponse({
                'success': False,
                'error': 'Solo administración puede editar una atención pasada.'
            })

        peso = request.POST.get('peso')
        edad = request.POST.get('edad')
        meses = request.POST.get('meses')
        temperatura = request.POST.get('temperatura')
        diagnostico = request.POST.get('diagnostico').capitalize()
        observaciones = request.POST.get('observaciones').capitalize()

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

@staff_member_required()
@require_POST
def cControl(request):
    try:
        agenda = Agenda.objects.get(pk=int(request.POST.get('id')))
        motivo = request.POST.get('cancelReason')

        agenda.estado = 'Cancelada'
        agenda.cancelado = motivo
        agenda.save()

        return JsonResponse({'success': 'Agenda cancelada.'})
    except Exception as e:
        return JsonResponse({'error': f"Error al cancelar agenda - Error: {e}"})



@login_required(login_url=LOGIN_URL)
@require_POST
def aDueno(request):
    data = {}
    try:
        nombre = request.POST.get('nombre').title()

        rut = request.POST.get('rut').upper()
        if not validar_rut(rut):
            return JsonResponse({"success": False,"error": "El RUT ingresado no es válido."}, status=400)
        
        correo = request.POST.get('correo').lower()
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion').title()

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


@login_required(login_url=LOGIN_URL)
@require_POST
def eUsuario(request):
    data = {}
    try:
        personal = Personal.objects.get(correo=request.user.email)
        telefono = request.POST.get('telefono')

        rut = request.POST.get('rut').upper()
        if not validar_rut(rut):
            return JsonResponse({"success": False,"error": "El RUT ingresado no es válido."}, status=400)

        with transaction.atomic():
            personal.nombre = request.POST.get('nombre').title()
            personal.rut = rut
            personal.correo = request.POST.get('correo').lower()
            personal.telefono = int(telefono) if telefono not in (None, '') else None
            personal.direccion = request.POST.get('direccion').title()
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


@login_required(login_url=LOGIN_URL)
@require_POST
def aPaciente(request):
    data = {}
    try:
        dueno = Dueno.objects.get(pk=int(request.POST.get('dueno')))
        edad = request.POST.get('edad')
        meses = request.POST.get('meses')
        nchip = request.POST.get('nchip')

        if Paciente.objects.filte(nchip=int(nchip)).exists():
            return JsonResponse({'error': 'Numero de chip ya registrado.'})

        with transaction.atomic():
            paciente = Paciente.objects.create(
                nchip = int(nchip) if nchip not in (None, '') else None,
                nombre = request.POST.get('nombre').title(),
                especie = request.POST.get('especie'),
                raza = request.POST.get('raza').title(),
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


@login_required(login_url=LOGIN_URL)
@require_POST
def ePaciente(request):
    data = {}
    try:
        paciente = Paciente.objects.get(pk=int(request.POST.get('id')))
        edad = request.POST.get('edad')
        meses = request.POST.get('meses')
        nchip = request.POST.get('nchip')
        dueno_id = request.POST.get('dueno')

        with transaction.atomic():
            paciente.nchip = int(nchip) if nchip not in (None, '') else None
            paciente.nombre = request.POST.get('nombre').title()
            paciente.especie = request.POST.get('especie')
            paciente.raza = request.POST.get('raza').title()
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


@login_required(login_url=LOGIN_URL)
@require_POST
def aVacunaPaciente(request):
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


@login_required(login_url=LOGIN_URL)
@require_POST
def aCirugiaPaciente(request):
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
# BODEGAS (solo administración)
#===================================================================================================================================================

@staff_member_required(login_url=LOGIN_URL)
@require_GET
def gBodegas(request):
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


@staff_member_required(login_url=LOGIN_URL)
@require_GET
def gBodegaInsumos(request, bodega_id):
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


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def aBodega(request):
    data = {}
    try:
        with transaction.atomic():
            bodega = Bodega.objects.create(
                nombre = request.POST.get('nombre').upper(),
                ubicacion = request.POST.get('ubicacion').upper(),
                encargado = request.POST.get('encargado').title()
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


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def eBodega(request):
    data = {}
    try:
        bodega = Bodega.objects.get(pk=int(request.POST.get('id')))
        with transaction.atomic():
            bodega.nombre = request.POST.get('nombre').upper()
            bodega.ubicacion = request.POST.get('ubicacion').upper()
            bodega.encargado = request.POST.get('encargado').title()
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


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def delBodega(request):
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
# INSUMOS / VACUNAS (INVENTARIO) - solo administración
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


@staff_member_required(login_url=LOGIN_URL)
@require_GET
def gInventario(request):
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


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def aInsumo(request):
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
                nombre = request.POST.get('nombre').title(),
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


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def eInsumo(request):
    data = {}
    try:
        insumo = Insumo.objects.get(pk=int(request.POST.get('id')))
        stock = request.POST.get('stock')
        precio = request.POST.get('precio')
        descuento = request.POST.get('descuento')
        ubicacion_id = request.POST.get('ubicacion')

        with transaction.atomic():
            insumo.nombre = request.POST.get('nombre').title()
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


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def delInsumo(request):
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
# PROCEDIMIENTOS (solo administración)
#===================================================================================================================================================

@staff_member_required(login_url=LOGIN_URL)
@require_POST
def aProcedimiento(request):
    data = {}
    try:
        precio = request.POST.get('precio')
        with transaction.atomic():
            proc = Procedimiento.objects.create(
                nombre = request.POST.get('nombre').title(),
                precio = int(precio) if precio not in (None, '') else None
            )
        data = {'success': True, 'data': {'id': proc.pk, 'nombre': proc.nombre, 'precio': proc.precio}}
    except Exception as e:
        print(f"Error al guardar procedimiento - Error: {e}")
        data = {'success': False, 'error': f"Error al registrar procedimiento - Error: {e}"}
    return JsonResponse(data)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def eProcedimiento(request):
    data = {}
    try:
        proc = Procedimiento.objects.get(pk=int(request.POST.get('id')))
        precio = request.POST.get('precio')
        with transaction.atomic():
            proc.nombre = request.POST.get('nombre').title()
            proc.precio = int(precio) if precio not in (None, '') else None
            proc.save()
        data = {'success': True, 'data': {'id': proc.pk, 'nombre': proc.nombre, 'precio': proc.precio}}
    except Exception as e:
        print(f"Error al editar procedimiento - Error: {e}")
        data = {'success': False, 'error': f"Error al editar procedimiento - Error: {e}"}
    return JsonResponse(data)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def delProcedimiento(request):
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
# ESPECIES (lectura general) Y RAZAS (lectura general, escritura solo administración)
#===================================================================================================================================================

@login_required(login_url=LOGIN_URL)
@require_GET
def gEspecies(request):
    try:
        especies = [{'id': e.pk, 'nombre': e.nombre} for e in Especie.objects.all()]
        return JsonResponse({'especies': especies})
    except Exception as e:
        print(f"Error al Obtener Datos - Error: {e}")
        return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def aEspecie(request):
    data = {}
    try:
        nombre = request.POST.get('nombre').title()
        if Especie.objects.filter(nombre = nombre).exists():
            data = {'success': False, 'error': "Especie ya existe en el sistema"}
            return JsonResponse(data)
        
        with transaction.atomic():
            especie = Especie.objects.create(nombre=nombre)
        data = {'success': True, 'data': {'id': especie.pk, 'nombre': especie.nombre}}
    except Exception as e:
        print(f"Error al guardar especie - Error: {e}")
        data = {'success': False, 'error': f"Error al registrar especie - Error: {e}"}
    return JsonResponse(data)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def eEspecie(request):
    data = {}
    try:
        especie = Especie.objects.get(pk=int(request.POST.get('id')))

        nombre = request.POST.get('nombre').title()
        if nombre != especie.nombre:
            if Especie.objects.filter(nombre = nombre).exists():
                data = {'success': False, 'error': "Especie ya existe en el sistema"}
                return JsonResponse(data)

        with transaction.atomic():
            especie.nombre = nombre
            especie.save()
        data = {'success': True, 'data': {'id': especie.pk, 'nombre': especie.nombre}}
    except Exception as e:
        print(f"Error al editar especie - Error: {e}")
        data = {'success': False, 'error': f"Error al editar especie - Error: {e}"}
    return JsonResponse(data)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def delEspecie(request):
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


@login_required(login_url=LOGIN_URL)
@require_GET
def gRazas(request):
    try:
        razas = [
            {'id': r.pk, 'nombre': r.nombre, 'especie_id': r.especie.pk}
            for r in Raza.objects.select_related('especie').all()
        ]
        return JsonResponse({'razas': razas})
    except Exception as e:
        print(f"Error al Obtener Datos - Error: {e}")
        return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def aRaza(request):
    data = {}
    try:
        especie = Especie.objects.get(pk=int(request.POST.get('especie')))
        nombre = request.POST.get('nombre').title()
        if Raza.objects.filter(nombre = nombre).exists():
            data = {'success': False, 'error': "Raza ya existe en el sistema"}
            return JsonResponse(data)
        
        with transaction.atomic():
            raza = Raza.objects.create(especie=especie, nombre=nombre)
        data = {'success': True, 'data': {'id': raza.pk, 'nombre': raza.nombre, 'especie_id': especie.pk}}
    except Exception as e:
        print(f"Error al guardar raza - Error: {e}")
        data = {'success': False, 'error': f"Error al registrar raza - Error: {e}"}
    return JsonResponse(data)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def eRaza(request):
    data = {}
    try:
        raza = Raza.objects.get(pk=int(request.POST.get('id')))
        especie_id = request.POST.get('especie')

        nombre = request.POST.get('nombre').title()
        if nombre != raza.nombre:
            if Raza.objects.filter(nombre = nombre).exists():
                data = {'success': False, 'error': "Raza ya existe en el sistema"}
                return JsonResponse(data)

        with transaction.atomic():
            raza.nombre = nombre
            if especie_id:
                raza.especie = Especie.objects.get(pk=int(especie_id))
            raza.save()
        data = {'success': True, 'data': {'id': raza.pk, 'nombre': raza.nombre, 'especie_id': raza.especie.pk}}
    except Exception as e:
        print(f"Error al editar raza - Error: {e}")
        data = {'success': False, 'error': f"Error al editar raza - Error: {e}"}
    return JsonResponse(data)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def delRaza(request):
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
# PERSONAL (solo administración)
#===================================================================================================================================================

@staff_member_required(login_url=LOGIN_URL)
@require_GET
def gPersonal(request):
    try:
        personal = [
            {
                'id': p.pk,
                'rut': p.rut,
                'nombre': p.nombre,
                'cargo': p.cargo,
                'telefono': p.telefono,
                'correo': p.correo,
                'direccion': p.direccion,
                'usuario': p.usuario,
                'activo': p.activo
            }
            for p in Personal.objects.all()
        ]
        return JsonResponse({'personal': personal})
    except Exception as e:
        print(f"Error al Obtener Datos - Error: {e}")
        return JsonResponse({'error': 'Error al Obtener Datos'}, status=404)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def aPersonal(request):
    data = {}
    try:
        telefono = request.POST.get('telefono')
        nombre = request.POST.get('nombre')

        rut = request.POST.get('rut').upper()
        if not validar_rut(rut):
            return JsonResponse({"success": False,"error": "El RUT ingresado no es válido."}, status=400)

        correo = request.POST.get('correo').strip().lower()
        if Personal.objects.filter(correo = correo).exists():
            data = {'success': False, 'error': "Correo ya registrado"}
            return JsonResponse(data)
        partes = (nombre or '').strip().split()

        cuenta_creada = False
        with transaction.atomic():
            username = _generar_username(nombre)
            personal = Personal.objects.create(
                rut = rut,
                nombre = nombre.title(),
                cargo = request.POST.get('cargo').title(),
                telefono = int(telefono) if telefono not in (None, '') else None,
                correo = correo,
                direccion = request.POST.get('direccion').title(),
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


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def ePersonal(request):
    data = {}
    try:
        personal = Personal.objects.get(pk=int(request.POST.get('id')))
        user = User.objects.get(email=personal.correo)


        telefono = request.POST.get('telefono')

        rut = request.POST.get('rut').upper()
        if not validar_rut(rut):
            return JsonResponse({"success": False,"error": "El RUT ingresado no es válido."}, status=400)

        correo = request.POST.get('correo').lower()
        if correo != personal.correo:
            if Personal.objects.filter(correo = correo).exists():
                data = {'success': False, 'error': "Correo ya registrado"}
                return JsonResponse(data)

        nombre = request.POST.get('nombre')
        partes = (nombre or '').strip().split()

        usuario = request.POST.get('usuario')

        with transaction.atomic():
            personal.rut = rut
            personal.nombre = nombre.title()
            personal.cargo = request.POST.get('cargo')
            personal.telefono = int(telefono) if telefono not in (None, '') else None
            personal.direccion = request.POST.get('direccion').title()
            personal.correo = correo
            personal.usuario = usuario
            personal.activo = request.POST.get('activo') or 'true'
            personal.save()

        

            user.username = usuario,
            user.email = correo,
            user.first_name = partes[0] if partes else '',
            user.last_name = ' '.join(partes[1:]) if len(partes) > 1 else ''
            user.save()

        data = {
            'success': True,
            'data': {
                'id': personal.pk, 'rut': personal.rut, 'nombre': personal.nombre,
                'cargo': personal.cargo, 'telefono': personal.telefono,
                'correo': personal.correo, 'direccion': personal.direccion, 'usuario': personal.usuario, 'activo': personal.activo
            }
        }
    except Exception as e:
        print(f"Error al editar personal - Error: {e}")
        data = {'success': False, 'error': f"Error al editar personal - Error: {e}"}
    return JsonResponse(data)


@staff_member_required(login_url=LOGIN_URL)
@require_POST
def delPersonal(request):
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


@login_required(login_url=LOGIN_URL)
@require_POST
def resetPassword(request):
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


def InsertarDatos(request):
    procedimientos = [
        # Abdominocentesis
        Procedimiento(nombre="Abdominocentesis C", precio=26300),
        Procedimiento(nombre="Abdominocentesis C", precio=39000),
        Procedimiento(nombre="Abdominocentesis C", precio=52500),
        Procedimiento(nombre="Abdominocentesis F", precio=21000),
        Procedimiento(nombre="Abdominocentesis F", precio=26300),

        # Abscesos
        Procedimiento(nombre="Abscesos Canino A", precio=21000),
        Procedimiento(nombre="Abscesos Canino B", precio=35000),
        Procedimiento(nombre="Abscesos Canino C", precio=47300),
        Procedimiento(nombre="Abscesos Felino A", precio=15800),
        Procedimiento(nombre="Abscesos Felino B", precio=25000),
        Procedimiento(nombre="Abscesos Felino C", precio=31500),

        # Amputación
        Procedimiento(nombre="Amputación Canina", precio=63000),
        Procedimiento(nombre="Amputación Canina", precio=93000),
        Procedimiento(nombre="Amputación Canina", precio=123000),
        Procedimiento(nombre="Amputación Canina", precio=153000),
        Procedimiento(nombre="Amputación Canina", precio=183000),
        Procedimiento(nombre="Amputación Canina", precio=210000),

        Procedimiento(nombre="Amputación Felina A", precio=52500),
        Procedimiento(nombre="Amputación Felina B", precio=69000),
        Procedimiento(nombre="Amputación Felina C", precio=84000),

        # Antiparasitarios
        Procedimiento(nombre="Antiparasitaria Oral", precio=2100),
        Procedimiento(nombre="Antiparasitario Gatos", precio=2100),
        Procedimiento(nombre="Antiparasitario Oral", precio=3200),
        Procedimiento(nombre="Antiparasitario Gatos", precio=1100),
        Procedimiento(nombre="Antiparasitario Rg.", precio=4800),
        Procedimiento(nombre="Antiparasitario Rg.", precio=5800),

        # Aseo quirúrgico
        Procedimiento(nombre="Aseo Quirúrgico + S", precio=21000),
        Procedimiento(nombre="Aseo Quirúrgico + S", precio=42000),
        Procedimiento(nombre="Aseo Quirúrgico + S", precio=48000),
        Procedimiento(nombre="Aseo Quirúrgico + S", precio=63000),
        Procedimiento(nombre="Aseo Quirúrgico + S", precio=73500),

        Procedimiento(nombre="Aseo Quirúrgico Canino", precio=21000),
        Procedimiento(nombre="Aseo Quirúrgico Canino", precio=41000),
        Procedimiento(nombre="Aseo Quirúrgico Canino", precio=63000),

        Procedimiento(nombre="Aseo Quirúrgico Felino", precio=15800),
        Procedimiento(nombre="Aseo Quirúrgico Felino", precio=30000),
        Procedimiento(nombre="Aseo Quirúrgico Felino", precio=30000),
        Procedimiento(nombre="Aseo Quirúrgico Felino", precio=42000),

        # Castración
        Procedimiento(nombre="Castración Criptorquídica", precio=31500),
        Procedimiento(nombre="Castración Criptorquídica", precio=36800),
        Procedimiento(nombre="Castración Criptorquídica", precio=42000),
        Procedimiento(nombre="Castración Criptorquídica", precio=52000),
        Procedimiento(nombre="Castración Criptorquídica", precio=73500),

        Procedimiento(nombre="Castración Monorquídica", precio=21000),
        Procedimiento(nombre="Castración Monorquídica", precio=26300),
        Procedimiento(nombre="Castración Monorquídica", precio=31500),
        Procedimiento(nombre="Castración Monorquídica", precio=39000),
        Procedimiento(nombre="Castración Monorquídica", precio=52500),

        # Caudectomía
        Procedimiento(nombre="Caudectomía Terapéutica", precio=21000),
        Procedimiento(nombre="Caudectomía Terapéutica", precio=31500),
        Procedimiento(nombre="Caudectomía Terapéutica", precio=36800),
        Procedimiento(nombre="Caudectomía Terapéutica", precio=48000),
        Procedimiento(nombre="Caudectomía Terapéutica", precio=63000),

        # Certificados
        Procedimiento(nombre="Certificado De Salud", precio=7400),
        Procedimiento(nombre="Certificado De Salud", precio=10500),

        # Cesáreas
        Procedimiento(nombre="Cesárea Canina A", precio=52500),
        Procedimiento(nombre="Cesárea Canina B", precio=82500),
        Procedimiento(nombre="Cesárea Canina C", precio=100500),
        Procedimiento(nombre="Cesárea Canina D", precio=126000),

        Procedimiento(nombre="Cesárea Felina A", precio=36800),
        Procedimiento(nombre="Cesárea Felina B", precio=47300),

        Procedimiento(nombre="Cesárea Radical Canina", precio=36800),
        Procedimiento(nombre="Cesárea Radical Canina", precio=56800),
        Procedimiento(nombre="Cesárea Radical Canina", precio=73500),
        Procedimiento(nombre="Cesárea Radical Felina", precio=26300),
        Procedimiento(nombre="Cesárea Radical Felina", precio=36800),

        # Cherry Eye
        Procedimiento(nombre="Cherry Eye Bilateral", precio=47300),
        Procedimiento(nombre="Cherry Eye Bilateral", precio=63000),
        Procedimiento(nombre="Cherry Eye Bilateral", precio=63000),
        Procedimiento(nombre="Cherry Eye Bilateral", precio=82000),
        Procedimiento(nombre="Cherry Eye Bilateral", precio=105000),

        Procedimiento(nombre="Cherry Eye Unilateral", precio=31500),
        Procedimiento(nombre="Cherry Eye Unilateral", precio=42000),
        Procedimiento(nombre="Cherry Eye Unilateral", precio=47300),
        Procedimiento(nombre="Cherry Eye Unilateral", precio=62000),
        Procedimiento(nombre="Cherry Eye Unilateral", precio=84000),
        Procedimiento(nombre="Cherry Eye Unilateral", precio=84000),

        # Cistotomía
        Procedimiento(nombre="Cistotomía Canina A", precio=63000),
        Procedimiento(nombre="Cistotomía Canina B", precio=83000),
        Procedimiento(nombre="Cistotomía Canina C", precio=105000),

        Procedimiento(nombre="Cistotomía Felina A", precio=42000),
        Procedimiento(nombre="Cistotomía Felina B", precio=52000),
        Procedimiento(nombre="Cistotomía Felina C", precio=63000),

        # Consultas
        Procedimiento(nombre="Consulta AE. EX.", precio=15800),
        Procedimiento(nombre="Consulta AE. SJ.", precio=10500),
        Procedimiento(nombre="Consulta EX.", precio=9500),
        Procedimiento(nombre="Consulta SJ.", precio=6300),

        # Controles
        Procedimiento(nombre="Control EX.", precio=3700),
        Procedimiento(nombre="Control SJ.", precio=2700),

        # Corte de uñas
        Procedimiento(nombre="Corte De Uñas EX.", precio=5250),
        Procedimiento(nombre="Corte De Uñas SJ.", precio=3700),

        # Curaciones
        Procedimiento(nombre="Curaciones Caninas", precio=5300),
        Procedimiento(nombre="Curaciones Caninas", precio=18000),
        Procedimiento(nombre="Curaciones Caninas", precio=26300),
        Procedimiento(nombre="Curaciones Felinas", precio=5300),
        Procedimiento(nombre="Curaciones Felinas", precio=15800),

        # Destartraje
        Procedimiento(nombre="Destartraje Canino", precio=21000),
        Procedimiento(nombre="Destartraje Canino", precio=41000),
        Procedimiento(nombre="Destartraje Canino", precio=63000),
        Procedimiento(nombre="Destartraje Felino", precio=21000),
        Procedimiento(nombre="Destartraje Felino", precio=31500),

        # Entropión
        Procedimiento(nombre="Entropión Bilateral", precio=47300),
        Procedimiento(nombre="Entropión Bilateral", precio=57800),
        Procedimiento(nombre="Entropión Bilateral", precio=73500),
        Procedimiento(nombre="Entropión Bilateral", precio=100000),
        Procedimiento(nombre="Entropión Bilateral", precio=126000),

        Procedimiento(nombre="Entropión Unilateral", precio=31500),
        Procedimiento(nombre="Entropión Unilateral", precio=42000),
        Procedimiento(nombre="Entropión Unilateral", precio=42000),
        Procedimiento(nombre="Entropión Unilateral", precio=58000),
        Procedimiento(nombre="Entropión Unilateral", precio=73500),

        # Enucleación
        Procedimiento(nombre="Enucleación Unilateral", precio=26300),
        Procedimiento(nombre="Enucleación Unilateral", precio=31500),
        Procedimiento(nombre="Enucleación Unilateral", precio=36800),
        Procedimiento(nombre="Enucleación Unilateral", precio=48000),
        Procedimiento(nombre="Enucleación Unilateral", precio=63000),

        # Epuli
        Procedimiento(nombre="Epuli", precio=8400),

        # Esterilización
        Procedimiento(nombre="Esterilización Canina", precio=21000),
        Procedimiento(nombre="Esterilización Canina", precio=26300),
        Procedimiento(nombre="Esterilización Canina", precio=36800),
        Procedimiento(nombre="Esterilización Canina", precio=36800),
        Procedimiento(nombre="Esterilización Canina", precio=42000),
        Procedimiento(nombre="Esterilización Canina", precio=52500),
        Procedimiento(nombre="Esterilización Canina", precio=52500),
        Procedimiento(nombre="Esterilización Canina", precio=63000),
        Procedimiento(nombre="Esterilización Canina", precio=68300),
        Procedimiento(nombre="Esterilización Canina", precio=78800),

        Procedimiento(nombre="Esterilización Felina", precio=15800),
        Procedimiento(nombre="Esterilización Felina", precio=21000),

        # Eutanasia
        Procedimiento(nombre="Eutanasia Previa A E.", precio=21000),
        Procedimiento(nombre="Eutanasia Previa A E.", precio=26300),
        Procedimiento(nombre="Eutanasia Previa A E.", precio=31000),
        Procedimiento(nombre="Eutanasia Previa A E.", precio=42000),
        Procedimiento(nombre="Eutanasia Previa A E.", precio=42000),
        Procedimiento(nombre="Eutanasia Previa A E.", precio=63000),

        # Falangectomía
        Procedimiento(nombre="Falangectomía Canina", precio=21000),
        Procedimiento(nombre="Falangectomía Canina", precio=31000),
        Procedimiento(nombre="Falangectomía Canina", precio=42000),

        Procedimiento(nombre="Falangectomía Felina", precio=15800),
        Procedimiento(nombre="Falangectomía Felina", precio=22000),
        Procedimiento(nombre="Falangectomía Felina", precio=31500),

        # Flushing
        Procedimiento(nombre="Flushing Felino", precio=12000),

        # Hemometra
        Procedimiento(nombre="Hemometra Canina A", precio=31500),
        Procedimiento(nombre="Hemometra Canina B", precio=51500),
        Procedimiento(nombre="Hemometra Canina C", precio=71500),
        Procedimiento(nombre="Hemometra Canina D", precio=94500),
        Procedimiento(nombre="Hemometra Felina A", precio=21000),
        Procedimiento(nombre="Hemometra Felina B", precio=31500),

        # Hernias
        Procedimiento(nombre="Hernia Inguinal Canina", precio=31500),
        Procedimiento(nombre="Hernia Inguinal Canina", precio=48000),
        Procedimiento(nombre="Hernia Inguinal Canina", precio=68300),
        Procedimiento(nombre="Hernia Inguinal Felina", precio=21000),
        Procedimiento(nombre="Hernia Inguinal Felina", precio=47300),

        Procedimiento(nombre="Hernia Perianal Bilateral", precio=63000),
        Procedimiento(nombre="Hernia Perianal Bilateral", precio=84000),
        Procedimiento(nombre="Hernia Perianal Bilateral", precio=104000),
        Procedimiento(nombre="Hernia Perianal Bilateral", precio=126000),

        Procedimiento(nombre="Hernia Perianal Canina", precio=47300),
        Procedimiento(nombre="Hernia Perianal Canina", precio=57300),
        Procedimiento(nombre="Hernia Perianal Canina", precio=68300),

        Procedimiento(nombre="Hernia Perianal Felina", precio=42000),
        Procedimiento(nombre="Hernia Perianal Felina", precio=47300),

        Procedimiento(nombre="Hernia Umbilical Canina", precio=21000),
        Procedimiento(nombre="Hernia Umbilical Canina", precio=42500),
        Procedimiento(nombre="Hernia Umbilical Felina", precio=15800),
        Procedimiento(nombre="Hernia Umbilical Felina", precio=26300),

        # Implantación de microchip
        Procedimiento(nombre="Implantación De Microchip", precio=7400),
        Procedimiento(nombre="Implantación De Microchip", precio=10500),

        # Laparotomía
        Procedimiento(nombre="Laparotomía Canina", precio=26300),
        Procedimiento(nombre="Laparotomía Canina", precio=39000),
        Procedimiento(nombre="Laparotomía Canina", precio=52500),
        Procedimiento(nombre="Laparotomía Felina", precio=21000),
        Procedimiento(nombre="Laparotomía Felina", precio=31500),

        # Lavado de oído
        Procedimiento(nombre="Lavado De Oído Canino", precio=21000),
        Procedimiento(nombre="Lavado De Oído Canino", precio=31000),
        Procedimiento(nombre="Lavado De Oído Canino", precio=42000),
        Procedimiento(nombre="Lavado De Oído Felino", precio=15800),
        Procedimiento(nombre="Lavado De Oído Felino", precio=26300),

        # Limpieza de heridas
        Procedimiento(nombre="Limpieza De Herida Simple", precio=6300),
        Procedimiento(nombre="Limpieza De Herida Simple", precio=7400),

        # Mastectomía
        Procedimiento(nombre="Mastectomía Línea Completa", precio=12600),
        Procedimiento(nombre="Mastectomía Línea Completa", precio=63000),
        Procedimiento(nombre="Mastectomía Línea Completa", precio=73500),
        Procedimiento(nombre="Mastectomía Línea Completa", precio=74000),
        Procedimiento(nombre="Mastectomía Línea Completa", precio=84000),
        Procedimiento(nombre="Mastectomía Línea Completa", precio=100000),

        # Sedación
        Procedimiento(nombre="Sedación Canina A", precio=5300),
        Procedimiento(nombre="Sedación Canina B", precio=10000),
        Procedimiento(nombre="Sedación Canina C", precio=15800),
        Procedimiento(nombre="Sedación Felina A", precio=5300),
        Procedimiento(nombre="Sedación Felina B", precio=10500),

        # Quimioterapia
        Procedimiento(nombre="Sesión De Quimioterapia", precio=15800),
        Procedimiento(nombre="Sesión De Quimioterapia", precio=21000),
        Procedimiento(nombre="Sesión De Quimioterapia", precio=31500),

        # Sondaje
        Procedimiento(nombre="Sondaje Urinario Felino", precio=21000),
        Procedimiento(nombre="Sondaje Urinario Canino", precio=26300),
        Procedimiento(nombre="Sondaje Urinario Canino", precio=38000),
        Procedimiento(nombre="Sondaje Urinario Canino", precio=52500),
        Procedimiento(nombre="Sondaje Urinario Felino", precio=31500),

        # Sutura
        Procedimiento(nombre="Sutura", precio=47300),
        Procedimiento(nombre="Sutura Canina A", precio=15800),
        Procedimiento(nombre="Sutura Canina B", precio=30000),
        Procedimiento(nombre="Sutura Felina A", precio=15800),
        Procedimiento(nombre="Sutura Felina B", precio=36800),

        # Toma de muestras
        Procedimiento(nombre="Toma De Muestras Externas", precio=6300),
        Procedimiento(nombre="Toma De Muestras Sangre", precio=5300),

        # Tratamientos inyectables
        Procedimiento(nombre="Tratamiento Inyectable 5 A", precio=3200),
        Procedimiento(nombre="Tratamiento Inyectable 1 A", precio=2100),
        Procedimiento(nombre="Tratamiento Inyectable 1 A", precio=3700),
        Procedimiento(nombre="Tratamiento Inyectable 10", precio=3700),
        Procedimiento(nombre="Tratamiento Inyectable 10", precio=3700),
        Procedimiento(nombre="Tratamiento Inyectable 5 A", precio=4200),
        Procedimiento(nombre="Tratamiento Inyectable De", precio=4200),
        Procedimiento(nombre="Tratamiento Inyectable De", precio=5300),

        # Tumores
        Procedimiento(nombre="Tumores Canino A", precio=21000),
        Procedimiento(nombre="Tumores Canino B", precio=41000),
        Procedimiento(nombre="Tumores Caninos C", precio=61000),
        Procedimiento(nombre="Tumores Caninos D", precio=81000),
        Procedimiento(nombre="Tumores Caninos E", precio=105000),
        Procedimiento(nombre="Tumores Felino A", precio=21000),
        Procedimiento(nombre="Tumores Felino B", precio=52500),

        # Vacunas
        Procedimiento(nombre="Vacuna Antirrábica", precio=9500),
        Procedimiento(nombre="Vacuna Antirrábica", precio=11600),
        Procedimiento(nombre="Vacuna Óctuple SJ", precio=9500),
        Procedimiento(nombre="Vacuna Óctuple", precio=11600),
        Procedimiento(nombre="Vacuna Triple Felina", precio=10500),
        Procedimiento(nombre="Vacuna Triple Felina", precio=12600),

        # Vendajes
        Procedimiento(nombre="Vendaje Canino A", precio=15800),
        Procedimiento(nombre="Vendaje Canino B", precio=31500),
        Procedimiento(nombre="Vendaje Felino A", precio=10500),
        Procedimiento(nombre="Vendaje Felino B", precio=21000),
    ]

    Procedimiento.objects.bulk_create(procedimientos)

    return JsonResponse({'success': 'Se insertaron los datos sin problema'})
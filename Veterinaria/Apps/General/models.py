from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone

# Create your models here.

class Bodega(models.Model):
    codigo = models.CharField(max_length=100, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    ubicacion = models.CharField(max_length=100, null=True, blank=True)
    encargado = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        txt = "Codigo: {0} - Nombre: {1} - Ubicacion: {2} - Encargado: {3}"
        return txt.format(self.codigo, self.nombre, self.ubicacion, self.encargado)

class Insumo(models.Model):
    codigo = models.CharField(max_length=100, null=True, blank=True)
    nombre = models.CharField(max_length=300, null=True, blank=True)
    tipo = models.CharField(max_length=50, null=True, blank=True)
    unidad = models.CharField(max_length=50, null=True, blank=True)
    stock = models.PositiveIntegerField(null=True, blank=True)
    precio = models.PositiveIntegerField(null=True, blank=True)
    descuento = models.PositiveIntegerField(null=True, blank=True)
    ubicacion = models.ForeignKey(Bodega, on_delete=models.SET_DEFAULT, default=1)

    def __str__(self):
        txt = "Codigo: {0} - Nombre: {1} - Tipo: {2} - Unidad: {3} - Stock: {4} - Precio {5} - Desc: {6} - Ubicacion: {7}"
        return txt.format(self.codigo, self.nombre, self.tipo, self.unidad, self.stock, self.precio, self.descuento, self.ubicacion.nombre)

class Procedimiento(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=True)
    precio = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        txt = "Nombre: {0} - Precio: {1}"
        return txt.format(self.nombre, self.precio)

class Especie(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre or ''

class Raza(models.Model):
    especie = models.ForeignKey(Especie, on_delete=models.CASCADE, related_name='razas')
    nombre = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        txt = "Raza: {0} - Especie: {1}"
        return txt.format(self.nombre, self.especie.nombre)

class Personal(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=True)
    rut = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.IntegerField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    cargo = models.CharField(max_length=100, null=True, blank=True)
    usuario = models.CharField(max_length=100, null=True, blank=True)
    activo = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        txt = "Nombre: {0} - Rut: {1} - Correo: {2} - Telefono: {3}"
        return txt.format(self.nombre, self.rut, self.correo, self.telefono)

class Dueno(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=True)
    rut = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.IntegerField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        txt = "Nombre: {0} - Rut: {1} - Correo: {2} - Telefono: {3}"
        return txt.format(self.nombre, self.rut, self.correo, self.telefono)


class Paciente(models.Model):
    nchip = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    especie = models.CharField(max_length=100, blank=True, null=True)
    raza = models.CharField(max_length=100, null=True, blank=True)
    genero = models.CharField(max_length=100, null=True, blank=True)
    edad = models.IntegerField(blank=True, null=True)
    meses = models.IntegerField(null=True, blank=True)
    peso = models.CharField(max_length=10, blank=True, null=True)
    marca = models.CharField(max_length=50, null=True, blank=True)
    estd_rep = models.CharField(max_length=50, null=True, blank=True)
    paricion = models.CharField(max_length=100, null=True, blank=True)
    datos = models.CharField(max_length=100, null=True, blank=True)
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE)
    fecha_ins = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        txt = "N°Chip: {0} - Nombre: {1} - Edad: {2} - Dueño: {3}"
        return txt.format(self.nchip, self.nombre, self.edad, self.dueno.nombre)

class VacunasPaciente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='vacunas')
    vacuna = models.ForeignKey(Insumo, on_delete=models.SET_DEFAULT, default=1)
    nombre = models.CharField(max_length=300, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)

    def __str__(self):
        txt = "ID: {0} - Paciente: {1} - ID Vacuna: {2} - Vacuna: {3} - Fecha: {4}"
        return txt.format(self.pk, self.paciente.nombre, self.vacuna.pk, self.nombre, self.fecha)


class CirugiasPaciente(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='cirugias')
    procedimiento = models.ForeignKey(Procedimiento, on_delete=models.SET_DEFAULT, default=1)
    nombre = models.CharField(max_length=300, null=True, blank=True)
    fecha = models.DateField(null=True, blank=True)

    def __str__(self):
        txt = "Paciente: {0} - Procedimiento: {1} - Fecha: {2}"
        return txt.format(self.paciente.nombre, self.nombre, self.fecha)


TIPO_AGENDA_CHOICES = [
    ('Atención Médica', 'Atención Médica'),
    ('Hospital', 'Hospital'),
    ('Quirúrgica', 'Quirúrgica'),
    ('Terreno', 'Terreno'),
    ('Tratamiento', 'Tratamiento'),
]


class Agenda(models.Model):
    origen = models.CharField(max_length=100, null=True, blank=True, default="Agenda")
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=50, blank=True, null=True, choices=TIPO_AGENDA_CHOICES)
    procedimiento = models.CharField(max_length=200, blank=True, null=True)
    datos_ing = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    peso = models.CharField(max_length=10, null=True, blank=True)
    edad = models.IntegerField(blank=True, null=True)
    meses = models.IntegerField(null=True, blank=True)
    temperatura = models.CharField(max_length=50, blank=True, null=True)
    diagnostico = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.CharField(max_length=800, blank=True, null=True)
    costo = models.IntegerField(blank=True, null=True)
    veterinario = models.CharField(max_length=200, blank=True, null=True) 
    id_vet = models.ForeignKey(Personal, on_delete=models.SET_DEFAULT, default=1)
    estado = models.CharField(max_length=100, null=True, blank=True,default="Pendiente")
    cancelado = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        txt = "ID: {0} - Mascota: {1} - Fecha: {2} - Hora: {3} - Estado: {4}"
        return txt.format(self.pk, self.paciente.nombre, self.fecha, self.hora, self.estado)

    @property
    def esta_expirado(self):
        if self.origen == 'Ingreso':
            return False
        ahora = timezone.localtime(timezone.now())
        limite = ahora - timedelta(hours=2)

        fecha_hora = datetime.combine(
            self.fecha,
            self.hora
        )

        fecha_hora = timezone.make_aware(
            fecha_hora,
            timezone.get_current_timezone()
        )

        return fecha_hora < limite

    def procesar_expiracion(self):
        if self.estado == 'Pendiente' and self.esta_expirado:
            self.estado = 'Cancelada'
            self.cancelado = 'Cancelada por Expiración'
            self.save()
            return True
        return False

    @classmethod
    def marcar_expirados(cls):
        expiradas = cls.objects.filter(estado='Pendiente')

        contador = 0
        for agendas in expiradas:
            agendas.procesar_expiracion()
            contador += 1
        
        return contador

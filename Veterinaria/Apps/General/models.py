from django.db import models

# Create your models here.

class Dueno(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=True)
    rut = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.IntegerField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        txt = "Nombre: {0} - Rut: {1} - Correo: {2} - Telefono: {3}"
        return txt.format(self.nombre, self.rut, self.correo, self.telefono)


class Mascota(models.Model):
    nchip = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    raza = models.CharField(max_length=100, null=True, blank=True)
    edad = models.IntegerField(blank=True, null=True)
    peso = models.IntegerField(blank=True, null=True)
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE)
    fecha_ins = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        txt = "N°Chip: {0} - Nombre: {1} - Edad: {2} - Dueño: {3}"
        return txt.format(self.nchip, self.nombre, self.edad, self.dueno.nombre)

class Control(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    diagnostico = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    peso = models.IntegerField(null=True, blank=True)
    observaciones = models.CharField(max_length=800, blank=True, null=True)

    def __str__(self):
        txt = "ID: {0} - Mascota: {1} - Fecha: {2} - Hora: {3}"
        return txt.format(self.pk, self.mascota.nombre, self.fecha, self.hora)



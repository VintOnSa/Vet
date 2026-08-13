from django.db import models

# Create your models here.

class Veterinario(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=True)
    rut = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.IntegerField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

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
    dueno = models.ForeignKey(Dueno, on_delete=models.CASCADE)
    fecha_ins = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        txt = "N°Chip: {0} - Nombre: {1} - Edad: {2} - Dueño: {3}"
        return txt.format(self.nchip, self.nombre, self.edad, self.dueno.nombre)

class Vacunas(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='vacunas')
    vacunas = models.CharField(max_length=300, null=True, blank=True)


class Control(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True, blank=True)
    procedimiento = models.CharField(max_length=200, blank=True, null=True)
    datos_ing = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    peso = models.CharField(max_length=10, null=True, blank=True)
    edad = models.CharField(max_length=50, null=True, blank=True)
    diagnostico = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.CharField(max_length=800, blank=True, null=True)
    costo = models.IntegerField(blank=True, null=True)
    veterinario = models.CharField(max_length=200, blank=True, null=True) 
    id_vet = models.ForeignKey(Veterinario, on_delete=models.SET_DEFAULT, default=1)
    estado = models.CharField(max_length=100, null=True, blank=True,default="Pendiente")

    def __str__(self):
        txt = "ID: {0} - Mascota: {1} - Fecha: {2} - Hora: {3} - Estado: {4}"
        return txt.format(self.pk, self.paciente.nombre, self.fecha, self.hora, self.estado)



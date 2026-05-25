from django.db import models
from django.contrib.auth.models import User
from apps.accounts.models import PerfilUsuario
from django.utils import timezone

class Medico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100, default='Medicina General')
    ubicacion_consultorio = models.CharField(max_length=255, help_text='Dirección del consultorio')
    def __str__(self):
        return f"Dr. {self.user.last_name}, {self.user.first_name}"

class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.get_full_name()

class Cita(models.Model):
    ESTADOS = (('programada','Programada'), ('cancelada','Cancelada'), ('completada','Completada'), ('pendiente_agendar','Pendiente de agendar'))
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas_paciente')
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)
    fecha_hora = models.DateTimeField()
    tipo = models.CharField(max_length=50, default='Medicina General')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='programada')
    motivo = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class HistoriaClinica(models.Model):
    paciente = models.ForeignKey(User, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    
class SolicitudAutorizacion(models.Model):
    TIPOS = (('cita_especialista','Cita especialista'), ('examen','Examen'), ('medicamento','Medicamento'))
    ESTADOS = (('pendiente','Pendiente'), ('aprobada','Aprobada'), ('rechazada','Rechazada'))
    paciente = models.ForeignKey(User, on_delete=models.CASCADE)
    medico_solicitante = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    motivo_rechazo = models.TextField(blank=True)
    especialidad_solicitada = models.CharField(max_length=100, blank=True)
    examen_solicitado = models.CharField(max_length=100, blank=True)
    medicamento_nombre = models.CharField(max_length=200, blank=True)
    medicamento_dosis = models.CharField(max_length=100, blank=True)
    medicamento_indicaciones = models.TextField(blank=True)

class FormulaMedicamento(models.Model):
    solicitud = models.OneToOneField(SolicitudAutorizacion, on_delete=models.CASCADE)
    paciente = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField(auto_now_add=True)

class FarmaciaAutorizada(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    latitud = models.FloatField()
    longitud = models.FloatField()
    telefono = models.CharField(max_length=20)
    def __str__(self):
        return self.nombre

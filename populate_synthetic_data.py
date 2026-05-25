import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'micita_eps.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from apps.accounts.models import PerfilUsuario
from apps.citas.models import Medico, Cita, FarmaciaAutorizada, SolicitudAutorizacion

def run():
    # Crear usuarios
    users_data = [
        ('ana.lopez', 'Ana', 'López', '1012345678', 'paciente', 'ana@mail.com', '3101234567', 'Calle 1 #2-3', 'Sura'),
        ('carlos.ruiz', 'Carlos', 'Ruiz', '1023456789', 'paciente', 'carlos@mail.com', '3209876543', 'Carrera 4 #5-6', 'Nueva EPS'),
        ('dra.martinez', 'Laura', 'Martínez', '2012345678', 'medico', 'laura@mail.com', '3112223344', 'Consultorio 101', 'Sura'),
        ('dr.gomez', 'Andrés', 'Gómez', '2023456789', 'medico', 'andres@mail.com', '3155556677', 'Consultorio 202', 'Sanitas'),
        ('autorizador1', 'Luis', 'Pérez', '3012345678', 'autorizador', 'luis@mail.com', '3001112233', 'Oficina central', 'EPS prueba'),
    ]
    for u in users_data:
        user, created = User.objects.get_or_create(username=u[0], defaults={
            'first_name': u[1], 'last_name': u[2], 'email': u[5]
        })
        if created:
            user.set_password('prueba123')
            user.save()
            perfil = user.perfilusuario
            perfil.documento = u[3]
            perfil.rol = u[4]
            perfil.telefono = u[6]
            perfil.direccion = u[7]
            perfil.eps = u[8]
            perfil.save()
            print(f"Usuario creado: {u[0]}")

    # Crear médicos
    for user in User.objects.filter(perfilusuario__rol='medico'):
        Medico.objects.get_or_create(user=user, defaults={
            'especialidad': 'Medicina General',
            'ubicacion_consultorio': user.perfilusuario.direccion
        })

    # Farmacias
    farmacias = [
        ("Farmatodo Chapinero", "Calle 63 #10-15", 4.6345, -74.0629, "6012345678"),
        ("Cruz Verde Centro", "Carrera 7 #21-40", 4.6097, -74.0699, "6019876543"),
        ("La Rebaja Usaquén", "Calle 119 #7-45", 4.7032, -74.0321, "6011122334"),
    ]
    for f in farmacias:
        FarmaciaAutorizada.objects.get_or_create(nombre=f[0], defaults={
            'direccion': f[1], 'latitud': f[2], 'longitud': f[3], 'telefono': f[4]
        })

    # Cita de ejemplo
    paciente_ana = User.objects.get(username='ana.lopez')
    medico_ejemplo = Medico.objects.first()
    if medico_ejemplo:
        Cita.objects.create(
            paciente=paciente_ana,
            medico=medico_ejemplo,
            fecha_hora=timezone.now() + timedelta(days=1, hours=10),
            tipo='Medicina General',
            estado='programada'
        )
        print("Cita de ejemplo creada")

    # Solicitud de medicamento pendiente
    medico_dra = Medico.objects.get(user__username='dra.martinez')
    SolicitudAutorizacion.objects.create(
        paciente=paciente_ana,
        medico_solicitante=medico_dra,
        tipo='medicamento',
        descripcion='Control de presión',
        medicamento_nombre='Losartán 50mg',
        medicamento_dosis='1 tableta cada 24h',
        medicamento_indicaciones='Tomar después del desayuno'
    )
    print("Datos sintéticos cargados.")

if __name__ == '__main__':
    run()

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.auth.models import User
from apps.accounts.models import PerfilUsuario
from .models import Medico, Cita, HistoriaClinica, SolicitudAutorizacion, FormulaMedicamento, FarmaciaAutorizada

def es_paciente(user):
    return hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'paciente'
def es_medico(user):
    return hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'medico'
def es_autorizador(user):
    return hasattr(user, 'perfilusuario') and user.perfilusuario.rol == 'autorizador'

@login_required
@user_passes_test(es_paciente)
def paciente_dashboard(request):
    perfil = request.user.perfilusuario
    citas_futuras = Cita.objects.filter(paciente=request.user, fecha_hora__gte=timezone.now(), estado='programada').order_by('fecha_hora')
    solicitudes_aprobadas = SolicitudAutorizacion.objects.filter(paciente=request.user, estado='aprobada', tipo='cita_especialista')
    formulas = FormulaMedicamento.objects.filter(paciente=request.user)
    manana = timezone.now().date() + timedelta(days=1)
    if Cita.objects.filter(paciente=request.user, fecha_hora__date=manana, estado='programada').exists():
        messages.info(request, "Tienes una cita para mañana. Te recordaremos 24h antes.")
    return render(request, 'citas/paciente_dashboard.html', {
        'perfil': perfil, 'citas_futuras': citas_futuras,
        'solicitudes_aprobadas': solicitudes_aprobadas, 'formulas': formulas,
        'now': timezone.now()
    })

@login_required
@user_passes_test(es_paciente)
def agendar_cita_general(request):
    if request.method == 'POST':
        fecha_str = request.POST['fecha']
        hora_str = request.POST['hora']
        medico_id = request.POST['medico']
        fecha_hora = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        fecha_hora = timezone.make_aware(fecha_hora)
        medico = get_object_or_404(Medico, id=medico_id)
        if Cita.objects.filter(medico=medico, fecha_hora=fecha_hora, estado='programada').exists():
            messages.error(request, "El médico ya tiene una cita en ese horario.")
        else:
            Cita.objects.create(paciente=request.user, medico=medico, fecha_hora=fecha_hora, tipo='Medicina General', estado='programada')
            messages.success(request, "Cita agendada. Recibirás recordatorio 24h antes.")
            return redirect('citas:paciente_dashboard')
    medicos = Medico.objects.all()
    return render(request, 'citas/agendar_cita.html', {'medicos': medicos})

@login_required
@user_passes_test(es_paciente)
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, paciente=request.user)
    if cita.fecha_hora > timezone.now() + timedelta(hours=24):
        cita.estado = 'cancelada'
        cita.save()
        messages.success(request, "Cita cancelada.")
    else:
        messages.error(request, "No se puede cancelar con menos de 24 horas.")
    return redirect('citas:paciente_dashboard')

@login_required
@user_passes_test(es_paciente)
def ver_formula(request, formula_id):
    formula = get_object_or_404(FormulaMedicamento, id=formula_id, paciente=request.user)
    farmacias = FarmaciaAutorizada.objects.all()
    return render(request, 'citas/formula_medicamento.html', {'formula': formula, 'farmacias': farmacias})

# MÉDICO
@login_required
@user_passes_test(es_medico)
def medico_dashboard(request):
    medico = Medico.objects.get(user=request.user)
    hoy = timezone.now().date()
    citas_hoy = Cita.objects.filter(medico=medico, fecha_hora__date=hoy, estado='programada').order_by('fecha_hora')
    pacientes_atendidos = set(c.paciente for c in citas_hoy)
    return render(request, 'citas/medico_dashboard.html', {
        'medico': medico, 'citas_hoy': citas_hoy, 'pacientes': pacientes_atendidos, 'hoy': hoy
    })

@login_required
@user_passes_test(es_medico)
def historia_clinica(request, paciente_id):
    paciente = get_object_or_404(User, id=paciente_id)
    if request.method == 'POST':
        diagnostico = request.POST['diagnostico']
        tratamiento = request.POST['tratamiento']
        medico = Medico.objects.get(user=request.user)
        HistoriaClinica.objects.create(paciente=paciente, medico=medico, diagnostico=diagnostico, tratamiento=tratamiento)
        messages.success(request, "Historia clínica actualizada.")
        return redirect('citas:medico_dashboard')
    historias = HistoriaClinica.objects.filter(paciente=paciente).order_by('-fecha')
    return render(request, 'citas/historia_clinica.html', {'paciente': paciente, 'historias': historias})

@login_required
@user_passes_test(es_medico)
def solicitar_especialista(request, paciente_id):
    if request.method == 'POST':
        especialidad = request.POST['especialidad']
        motivo = request.POST['motivo']
        medico = Medico.objects.get(user=request.user)
        SolicitudAutorizacion.objects.create(paciente=get_object_or_404(User, id=paciente_id), medico_solicitante=medico,
            tipo='cita_especialista', descripcion=motivo, especialidad_solicitada=especialidad)
        messages.success(request, "Solicitud enviada al autorizador.")
        return redirect('citas:medico_dashboard')
    return render(request, 'citas/solicitar_especialista.html', {'paciente_id': paciente_id})

@login_required
@user_passes_test(es_medico)
def solicitar_examen(request, paciente_id):
    if request.method == 'POST':
        examen = request.POST['examen']
        motivo = request.POST['motivo']
        medico = Medico.objects.get(user=request.user)
        SolicitudAutorizacion.objects.create(paciente=get_object_or_404(User, id=paciente_id), medico_solicitante=medico,
            tipo='examen', descripcion=motivo, examen_solicitado=examen)
        messages.success(request, "Solicitud de examen enviada.")
        return redirect('citas:medico_dashboard')
    return render(request, 'citas/solicitar_examen.html', {'paciente_id': paciente_id})

@login_required
@user_passes_test(es_medico)
def solicitar_medicamento(request, paciente_id):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        dosis = request.POST['dosis']
        indicaciones = request.POST['indicaciones']
        medico = Medico.objects.get(user=request.user)
        SolicitudAutorizacion.objects.create(paciente=get_object_or_404(User, id=paciente_id), medico_solicitante=medico,
            tipo='medicamento', descripcion='Receta', medicamento_nombre=nombre, medicamento_dosis=dosis, medicamento_indicaciones=indicaciones)
        messages.success(request, "Solicitud de medicamento enviada.")
        return redirect('citas:medico_dashboard')
    return render(request, 'citas/solicitar_medicamento.html', {'paciente_id': paciente_id})

# AUTORIZADOR
@login_required
@user_passes_test(es_autorizador)
def autorizador_dashboard(request):
    solicitudes = SolicitudAutorizacion.objects.filter(estado='pendiente').order_by('-fecha_solicitud')
    return render(request, 'citas/autorizador_dashboard.html', {'solicitudes': solicitudes})

@login_required
@user_passes_test(es_autorizador)
def aprobar_solicitud(request, sol_id):
    solicitud = get_object_or_404(SolicitudAutorizacion, id=sol_id)
    solicitud.estado = 'aprobada'
    solicitud.fecha_aprobacion = timezone.now()
    solicitud.save()
    if solicitud.tipo == 'cita_especialista':
        medico_esp = Medico.objects.first()
        Cita.objects.create(paciente=solicitud.paciente, medico=medico_esp,
            fecha_hora=timezone.now() + timedelta(days=7), tipo=f"Especialista: {solicitud.especialidad_solicitada}", estado='pendiente_agendar')
    elif solicitud.tipo == 'medicamento':
        FormulaMedicamento.objects.create(solicitud=solicitud, paciente=solicitud.paciente)
    messages.success(request, "Solicitud aprobada.")
    return redirect('citas:autorizador_dashboard')

@login_required
@user_passes_test(es_autorizador)
def rechazar_solicitud(request, sol_id):
    solicitud = get_object_or_404(SolicitudAutorizacion, id=sol_id)
    if request.method == 'POST':
        solicitud.estado = 'rechazada'
        solicitud.motivo_rechazo = request.POST['motivo']
        solicitud.save()
        messages.warning(request, "Solicitud rechazada.")
        return redirect('citas:autorizador_dashboard')
    return render(request, 'citas/rechazar_solicitud.html', {'solicitud': solicitud})

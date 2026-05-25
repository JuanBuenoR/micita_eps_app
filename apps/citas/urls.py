from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    path('paciente/', views.paciente_dashboard, name='paciente_dashboard'),
    path('agendar/', views.agendar_cita_general, name='agendar_cita'),
    path('cancelar/<int:cita_id>/', views.cancelar_cita, name='cancelar_cita'),
    path('formula/<int:formula_id>/', views.ver_formula, name='ver_formula'),
    path('medico/', views.medico_dashboard, name='medico_dashboard'),
    path('historia/<int:paciente_id>/', views.historia_clinica, name='historia_clinica'),
    path('solicitar_especialista/<int:paciente_id>/', views.solicitar_especialista, name='solicitar_especialista'),
    path('solicitar_examen/<int:paciente_id>/', views.solicitar_examen, name='solicitar_examen'),
    path('solicitar_medicamento/<int:paciente_id>/', views.solicitar_medicamento, name='solicitar_medicamento'),
    path('autorizador/', views.autorizador_dashboard, name='autorizador_dashboard'),
    path('aprobar/<int:sol_id>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar/<int:sol_id>/', views.rechazar_solicitud, name='rechazar_solicitud'),
]

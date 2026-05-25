from django.contrib import admin
from .models import Medico, Cita, HistoriaClinica, SolicitudAutorizacion, FormulaMedicamento, FarmaciaAutorizada
admin.site.register(Medico)
admin.site.register(Cita)
admin.site.register(HistoriaClinica)
admin.site.register(SolicitudAutorizacion)
admin.site.register(FormulaMedicamento)
admin.site.register(FarmaciaAutorizada)
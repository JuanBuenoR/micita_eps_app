from django.urls import path
from . import views

urlpatterns = [
    path('perfil/', views.editar_perfil, name='editar_perfil'),
]
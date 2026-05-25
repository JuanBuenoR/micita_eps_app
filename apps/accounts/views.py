from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import PerfilUsuario

def login_view(request):
    if request.user.is_authenticated:
        return redirect_rol(request.user)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect_rol(user)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def registro(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        nombres = request.POST['nombres']
        apellidos = request.POST['apellidos']
        documento = request.POST['documento']
        telefono = request.POST['telefono']
        eps = request.POST['eps']
        rol = request.POST.get('rol', 'paciente')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe')
            return redirect('registro')
        if PerfilUsuario.objects.filter(documento=documento).exists():
            messages.error(request, 'El documento ya está registrado')
            return redirect('registro')
        
        user = User.objects.create_user(username=username, password=password, email=email, first_name=nombres, last_name=apellidos)
        perfil = user.perfilusuario
        perfil.documento = documento
        perfil.telefono = telefono
        perfil.eps = eps
        perfil.rol = rol
        perfil.save()
        messages.success(request, 'Usuario creado. Ya puede iniciar sesión.')
        return redirect('login')
    return render(request, 'accounts/registro.html')

def redirect_rol(user):
    perfil = user.perfilusuario
    if perfil.rol == 'paciente':
        return redirect('citas:paciente_dashboard')
    elif perfil.rol == 'medico':
        return redirect('citas:medico_dashboard')
    elif perfil.rol == 'autorizador':
        return redirect('citas:autorizador_dashboard')
    return redirect('login')

@login_required
def editar_perfil(request):
    perfil = request.user.perfilusuario
    if request.method == 'POST':
        perfil.telefono = request.POST['telefono']
        perfil.direccion = request.POST['direccion']
        perfil.eps = request.POST['eps']
        perfil.save()
        messages.success(request, 'Perfil actualizado')
        return redirect_rol(request.user)
    return render(request, 'accounts/perfil.html', {'perfil': perfil})

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('registro/', accounts_views.registro, name='registro'),
    path('accounts/', include('apps.accounts.urls')),
    path('citas/', include('apps.citas.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

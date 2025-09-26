# Router y URLs para la API REST de resultados de módulos
from rest_framework import routers
from .api_views import ResultadoModuloViewSet

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

router = routers.DefaultRouter()

# Registrar el ViewSet con el router
router.register(r'resultadosmodulos', ResultadoModuloViewSet, basename='resultadosModulos')

urlpatterns = [
    # Tus patrones de URL van aquí
    # Ejemplo:
    # path('', views.index, name='index'),
    path('', views.index_view, name='index_view'),                                          #index que yo defino, aqui va la busqueda y los graficos
    path('auth/', views.auth_view, name='auth_view'),                                       #retorna la pagina sin mas
    path('login/', views.LoginViewCustom.as_view(), name='login_view'),                     #ocupa vista predefinida
    path('register/', views.register_view, name='register_view'),                           #vista que yo defino
    path('logout/', views.logout_view, name='logout_view'),                                 #ocupa vista predefinida


    # Las siguientes vistas son para configurar mas adelante
    # Vistas para recuperación de contraseña
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html'
    ), name='password_reset'),
    
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html'
         ), name='password_reset_confirm'),
    
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),

]

# Incluir las URLs del router de la API REST
urlpatterns += router.urls
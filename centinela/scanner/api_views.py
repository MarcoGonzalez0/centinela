# DJRF ViewSets para la API REST de la aplicación scanner
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

# Modelos
from .models import resultadoModulo, Escaneo, User


# Serializador para perfil de usuario
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']



# Viewset para User
# Serializador
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_active', 'date_joined']

# ViewSet
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    """
    Este ViewSet permite a los usuarios autenticados ver la lista de usuarios.
    Solo los administradores pueden acceder a esta vista.
    """

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:  # si es admin
            return User.objects.all() # devolver todos los usuarios
        else:
            return User.objects.filter(id=user.id)  # usuarios normales solo ven su propio usuario 
        
    """
    Las acciones me permiten definir endpoints personalizados dentro del ViewSet
    En este caso el endpoint /users/me/ permite al usuario autenticado obtener o actualizar su propio perfil.
    Notar que usa un serializador diferente para no exponer campos sensibles.
    Le estoy diciendo a DJRF: Agrega un nuevo endpoint llamado /users/me/ dentro del ViewSet UserViewSet, 
        que se pueda acceder sin ID (detail=False), acepte métodos GET y PATCH, y use el serializer UserProfileSerializer.
    """
    @action(detail=False, methods=['get', 'patch'], url_path='me', serializer_class=UserProfileSerializer)
    def me(self, request, *args, **kwargs):
        """
        Acción personalizada para obtener los detalles del usuario autenticado.
        URL: /users/me/
        Método: GET
        """
        user = request.user
               
        if request.method == 'PATCH':
            serializer=self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)

# ViewSet para Escaneo
# Serializador
class EscaneoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escaneo
        fields = ['id', 'user', 'objetivo', 'tipo_objetivo', 'fecha_inicio', 'fecha_fin', 'estado']

# ViewSet para Escaneo
class EscaneoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EscaneoSerializer
    """
    Este ViewSet permite a los usuarios autenticados ver sus escaneos.
    Los administradores pueden ver todos los escaneos, mientras que los usuarios normales solo pueden ver los suyos.
    """

    def get_queryset(self):
        qs = Escaneo.objects.all()

        if not self.request.user.is_staff:  # si no es admin
            qs = qs.filter(user=self.request.user)

        return qs



# ViewSet para resultadoModulo
# Serializador
class ResultadoModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = resultadoModulo
        fields = ['id', 'escaneo', 'nombre_modulo', 'estado', 'resultado', 'fecha_ejecucion', 'analisis_ia']

# ViewSet
class ResultadoModuloViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultadoModuloSerializer
    """
    Este ViewSet permite a los usuarios autenticados ver los resultados de los módulos.
    Los administradores pueden ver todos los resultados, mientras que los usuarios normales solo pueden ver los resultados de sus propios escaneos.
    """

    def get_queryset(self):
        qs = resultadoModulo.objects.all()

        if not self.request.user.is_staff:  # si no es admin
            qs = qs.filter(escaneo__user=self.request.user)

        escaneo_id = self.request.query_params.get('escaneo_id') # filtrar por escaneo_id si se proporciona(todos los modulos de X escaneo)
        if escaneo_id:
            qs = qs.filter(escaneo__id=escaneo_id)

        return qs



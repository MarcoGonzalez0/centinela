# DJRF ViewSets para la API REST de la aplicación scanner
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

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
        Acción personalizada para obtener o actualizar el perfil del usuario autenticado.
        URL: /api/users/me/
        Métodos: GET (obtener), PATCH (actualizar parcialmente)
        """
        user = request.user # Objeto Python: <User: juan>
               
        if request.method == 'PATCH':
            # DESERIALIZACIÓN: Validar y preparar datos para actualizar
            # request.data es un diccionario Python con los datos enviados
            # Ejemplo: {'username': 'juan2', 'email': 'nuevo@email.com'}
            serializer=self.get_serializer(user, data=request.data, partial=True) 

            serializer.is_valid(raise_exception=True) # Valida los datos según las reglas del modelo y serializer
            serializer.save() # Internamente ejecuta: UPDATE users SET ... WHERE id = user.id | Guarda los cambios en la BD

            # SERIALIZACIÓN: Convierte el objeto User actualizado a diccionario Python
            # serializer.data = {'id': 1, 'username': 'juan2', 'email': 'nuevo@email.com', ...}
            # DRF lo convierte a JSON antes de enviarlo al cliente
            return Response(serializer.data)
        
        # Método GET: Solo lectura
        # SERIALIZACIÓN: Convierte el objeto User a diccionario Python
        serializer = self.get_serializer(user) 
        return Response(serializer.data) # serializer.data es un dict con los datos del usuario

# ViewSet para Escaneo
# Serializador
class EscaneoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')  # campo adicional para mostrar el nombre de usuario
    email = serializers.EmailField(source='user.email')      # campo adicional para mostrar el email del usuario
    class Meta:
        model = Escaneo
        fields = ['id', 'user', 'username', 'email', 'objetivo', 'tipo_objetivo', 'fecha_inicio', 'fecha_fin', 'estado']

# Clase de paginación personalizada
class EscaneoPagination(PageNumberPagination):
    page_size = 10  # 10 escaneos por página
    page_size_query_param = 'page_size' # permite al cliente definir el tamaño de página
    max_page_size = 50 # máximo 50 escaneos por página

# ViewSet para Escaneo
class EscaneoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EscaneoSerializer
    pagination_class = EscaneoPagination
    """
    Este ViewSet permite a los usuarios autenticados ver sus escaneos.
    Los administradores pueden ver todos los escaneos, mientras que los usuarios normales solo pueden ver los suyos.
    """

    def get_queryset(self):
        qs = Escaneo.objects.all() # QuerySet inicial con todos los escaneos

        if not self.request.user.is_staff:  # si no es admin
            qs = qs.filter(user=self.request.user) # se filtran solo los escaneos del usuario autenticado

        # Filtros opcionales por parámetros de consulta
        # por estado (completado, en_proceso, pendiente, error)
        estado = self.request.query_params.get('estado') # filtrar por estado si se proporciona
        if estado:
            qs = qs.filter(estado=estado)

        # por objetivo (hola.cl, ejemplo.com)
        objetivo = self.request.query_params.get('objetivo') # filtrar por objetivo si se proporciona
        if objetivo:
            qs = qs.filter(objetivo__icontains=objetivo)

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



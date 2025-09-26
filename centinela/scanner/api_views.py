from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from .models import resultadoModulo

# Serializador
class ResultadoModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = resultadoModulo
        fields = ['id', 'escaneo', 'nombre_modulo', 'estado', 'resultado', 'fecha_ejecucion']

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

        escaneo_id = self.request.query_params.get('escaneo_id')
        if escaneo_id:
            qs = qs.filter(escaneo__id=escaneo_id)

        return qs

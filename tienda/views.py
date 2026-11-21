import django_filters
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

from .models import Categoria, Producto, Orden
from .serializers import (
    CategoriaSerializer,
    ProductoSerializer,
    RegistroUsuarioSerializer,
    OrdenSerializer,
)

class ProductoFilter(django_filters.FilterSet):
    talla = django_filters.CharFilter(field_name='variantes__talla', lookup_expr='iexact')

    class Meta:
        model = Producto
        fields = ['categoria', 'talla']

class RegistroUsuarioView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().distinct().order_by('-id')
    serializer_class = ProductoSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductoFilter
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'id']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorito(self, request, pk=None):
        producto = self.get_object()
        usuario = request.user

        if producto.favoritos.filter(id=usuario.id).exists():
            producto.favoritos.remove(usuario)
            return Response({
                'status': 'eliminado de favoritos',
                'es_favorito': False,
                'total_favoritos': producto.favoritos.count()
            }, status=status.HTTP_200_OK)
        else:
            producto.favoritos.add(usuario)
            return Response({
                'status': 'agregado a favoritos',
                'es_favorito': True,
                'total_favoritos': producto.favoritos.count()
            }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mis_favoritos(self, request):
        productos = request.user.productos_favoritos.all()
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)

class OrdenViewSet(viewsets.ModelViewSet):
    serializer_class = OrdenSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return Orden.objects.filter(usuario=self.request.user).prefetch_related('detalles__producto')
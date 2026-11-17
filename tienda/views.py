from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User

from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer, RegistroUsuarioSerializer

class RegistroUsuarioView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('-id')
    serializer_class = ProductoSerializer
    
    # Habilitar búsqueda, filtros exactos y ordenamiento
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['categoria', 'talla']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'id']

    # CUSTOM ACTION: Marcar o desmarcar un producto como favorito
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

    # CUSTOM ACTION EXTRA: Listar solo los favoritos del usuario autenticado
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mis_favoritos(self, request):
        productos = request.user.productos_favoritos.all()
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)
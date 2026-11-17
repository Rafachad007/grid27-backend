from rest_framework import viewsets
from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer

# Esta vista crea TODO el CRUD automático para las Categorías
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

# Esta vista crea TODO el CRUD automático para los Productos
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
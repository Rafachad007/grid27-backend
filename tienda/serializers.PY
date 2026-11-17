from rest_framework import serializers
from .models import Categoria, Producto, ImagenProducto

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ['id', 'imagen']

class ProductoSerializer(serializers.ModelSerializer):
    # AQUÍ ESTÁ EL REQUISITO DEL PROFESOR: Serializers Anidados.
    # En lugar de mandar el ID de la categoría, mandamos la categoría completa.
    categoria = CategoriaSerializer(read_only=True)
    # Mandamos todas las fotos anidadas dentro del producto.
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    
    # Este campo lo agregamos para facilitar que envíes el ID de la categoría cuando creas un producto nuevo
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', write_only=True
    )

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 
            'talla', 'stock', 'categoria', 'categoria_id', 'imagenes'
        ]
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Categoria, Producto, ImagenProducto

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'password']

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            password=validated_data['password']
        )

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']

class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ['id', 'imagen']

class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', write_only=True
    )
    es_favorito = serializers.SerializerMethodField()
    total_favoritos = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 
            'talla', 'stock', 'categoria', 'categoria_id', 
            'imagenes', 'es_favorito', 'total_favoritos'
        ]

    # Validaciones de negocio
    def validate_nombre(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("El nombre de la prenda debe tener al menos 3 caracteres.")
        return value

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio de la prenda debe ser mayor a $0.00 MXN.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El inventario (stock) no puede ser negativo.")
        return value

    def get_es_favorito(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favoritos.filter(id=request.user.id).exists()
        return False

    def get_total_favoritos(self, obj):
        return obj.favoritos.count()
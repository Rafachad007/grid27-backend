from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Categoria, Producto, VarianteProducto, ImagenProducto, Orden, DetalleOrden

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

class VarianteProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VarianteProducto
        fields = ['id', 'talla', 'stock']

class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ['id', 'imagen']

class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    variantes = VarianteProductoSerializer(many=True, read_only=True)
    imagenes = ImagenProductoSerializer(many=True, read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', write_only=True
    )
    stock_total = serializers.ReadOnlyField()
    es_favorito = serializers.SerializerMethodField()
    total_favoritos = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio',
            'categoria', 'categoria_id', 'variantes', 'stock_total',
            'imagenes', 'es_favorito', 'total_favoritos'
        ]

    def validate_nombre(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("El nombre de la prenda debe tener al menos 3 caracteres.")
        return value

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio de la prenda debe ser mayor a $0.00 MXN.")
        return value

    def get_es_favorito(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favoritos.filter(id=request.user.id).exists()
        return False

    def get_total_favoritos(self, obj):
        return obj.favoritos.count()

class ItemOrdenInputSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    talla = serializers.CharField(max_length=5)
    cantidad = serializers.IntegerField(min_value=1)

class DetalleOrdenSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleOrden
        fields = ['id', 'producto_nombre', 'talla', 'cantidad', 'precio_unitario']

class OrdenSerializer(serializers.ModelSerializer):
    items = ItemOrdenInputSerializer(many=True, write_only=True)
    detalles = DetalleOrdenSerializer(many=True, read_only=True)

    class Meta:
        model = Orden
        fields = ['id', 'fecha', 'direccion_envio', 'total', 'estado', 'items', 'detalles']
        read_only_fields = ['id', 'fecha', 'total', 'estado', 'detalles']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("El carrito está vacío.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        usuario = self.context['request'].user
        orden = Orden.objects.create(
            usuario=usuario,
            direccion_envio=validated_data['direccion_envio'],
            total=Decimal('0.00')
        )

        total_orden = Decimal('0.00')

        for item in items_data:
            try:
                variante = VarianteProducto.objects.select_for_update().get(
                    producto_id=item['producto_id'],
                    talla=item['talla']
                )
            except VarianteProducto.DoesNotExist:
                raise serializers.ValidationError(
                    f"La talla {item['talla']} no está disponible para este producto."
                )

            if variante.stock < item['cantidad']:
                raise serializers.ValidationError(
                    f"Stock insuficiente para {variante.producto.nombre} (Talla {item['talla']}). Disponibles: {variante.stock}."
                )

            variante.stock -= item['cantidad']
            variante.save()

            precio_unit = variante.producto.precio
            total_orden += precio_unit * item['cantidad']

            DetalleOrden.objects.create(
                orden=orden,
                producto=variante.producto,
                talla=item['talla'],
                cantidad=item['cantidad'],
                precio_unitario=precio_unit
            )

        orden.total = total_orden
        orden.save()
        return orden
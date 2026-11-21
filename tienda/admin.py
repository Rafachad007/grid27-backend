from django.contrib import admin
from .models import Categoria, Producto, VarianteProducto, ImagenProducto, Orden, DetalleOrden

class VarianteProductoInline(admin.TabularInline):
    model = VarianteProducto
    extra = 3

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'categoria', 'stock_total']
    list_filter = ['categoria']
    search_fields = ['nombre', 'descripcion']
    inlines = [VarianteProductoInline, ImagenProductoInline]

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']

class DetalleOrdenInline(admin.TabularInline):
    model = DetalleOrden
    extra = 0
    readonly_fields = ['producto', 'talla', 'cantidad', 'precio_unitario']

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'fecha', 'total', 'estado']
    list_filter = ['estado', 'fecha']
    search_fields = ['usuario__username', 'direccion_envio']
    inlines = [DetalleOrdenInline]
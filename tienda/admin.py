from django.contrib import admin
from .models import Categoria, Producto, ImagenProducto

# Esto es para poder subir varias fotos al mismo tiempo dentro del mismo producto
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

# Configuramos cómo se verá la tabla de productos
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria')
    list_filter = ('categoria', 'talla')
    search_fields = ('nombre', 'descripcion')
    inlines = [ImagenProductoInline]

# Registramos todo
admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)
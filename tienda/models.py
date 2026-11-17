from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    # Definimos las tallas disponibles
    TALLAS = [
        ('S', 'Chica'),
        ('M', 'Mediana'),
        ('L', 'Grande'),
        ('XL', 'Extra Grande'),
        ('U', 'Unitalla'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    talla = models.CharField(max_length=2, choices=TALLAS, default='U')
    stock = models.IntegerField(default=0)
    
    # Relación: Un producto pertenece a una categoría (ForeignKey)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')

    def __str__(self):
        return self.nombre

class ImagenProducto(models.Model):
    # Relación: Una imagen pertenece a un producto. Un producto puede tener muchas imágenes.
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/')

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"
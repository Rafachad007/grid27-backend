from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    favoritos = models.ManyToManyField(User, related_name='productos_favoritos', blank=True)

    @property
    def stock_total(self):
        return sum(v.stock for v in self.variantes.all())

    def __str__(self):
        return self.nombre

class VarianteProducto(models.Model):
    TALLAS_CHOICES = [
        ('S', 'S (Chica)'),
        ('M', 'M (Mediana)'),
        ('L', 'L (Grande)'),
        ('XL', 'XL (Extra Grande)'),
        ('U', 'Unitalla'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='variantes')
    talla = models.CharField(max_length=5, choices=TALLAS_CHOICES)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('producto', 'talla')
        verbose_name = 'Talla y Stock'
        verbose_name_plural = 'Tallas y Stock disponible'

    def __str__(self):
        return f"{self.producto.nombre} - Talla {self.talla} ({self.stock} pzas)"

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/')

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"

class Orden(models.Model):
    ESTADOS = [
        ('CONFIRMADA', 'Confirmada'),
        ('ENVIADA', 'Enviada'),
        ('ENTREGADA', 'Entregada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ordenes')
    fecha = models.DateTimeField(auto_now_add=True)
    direccion_envio = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='CONFIRMADA')

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Orden de Compra'
        verbose_name_plural = 'Órdenes de Compra'

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username} (${self.total})"

class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    talla = models.CharField(max_length=5)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} ({self.talla})"
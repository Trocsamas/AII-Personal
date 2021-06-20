from django.db import models
from django.shortcuts import reverse

# Create your models here.
class Universidad(models.Model):

    nombre = models.CharField(max_length=150, unique=True)
    logo = models.ImageField(upload_to='universidades')
    localidad = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("universidades:univesidad-detail", kwargs={"pk": self.pk})

class Centro(models.Model):

    nombre = models.CharField(max_length=150)
    localidad = models.CharField(max_length=50)
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE)
    class Meta:
        unique_together = [['nombre', 'localidad']]
    def __str__(self):
        return self.nombre + " - " + self.universidad.nombre

    def get_absolute_url(self):
        return reverse("Centro_detail", kwargs={"pk": self.pk})

class Grado(models.Model):
    nombre = models.CharField(max_length=150)
    nota_acceso = models.FloatField(null=True, blank=True)
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE)
    rama_conocimiento = models.CharField(max_length=50, null=True, blank=True)
    class Meta:
        ordering = ('centro',)
        unique_together = [['nombre', 'centro']]
    def __str__(self):
        return self.nombre
    def get_absolute_url(self):
        return reverse("universidades:grado-detail", kwargs={"pk": self.pk})

    def get_id(self):
        return self.pk

class Departamento(models.Model):

    nombre = models.CharField(max_length=150)
    centro = models.ForeignKey(Centro, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ('centro',)
        unique_together = [['nombre', 'centro']]

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("Departamento_detail", kwargs={"pk": self.pk})

class Asignatura(models.Model):

    nombre = models.CharField(max_length=150)
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
    curso = models.IntegerField(null=True, blank=True)
    codigo = models.CharField(max_length=10, unique=True)
    creditos = models.FloatField(null=True, blank=True)
    tipo_asignatura = models.CharField(max_length=50)
    duracion = models.CharField(max_length=20, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null = True, blank=True)


    class Meta:
        # Esto es debido a que en algunas universidades una asignatura
        # se repite en distintos grados sin cambiar el codigo por tanto
        # si hacemos unique together no hay más problemas
    
        unique_together = [['codigo', 'grado']]

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse("Asignatura_detail", kwargs={"pk": self.pk})

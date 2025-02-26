from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Create your models here.

    

class Mascotas(models.Model):
    Id = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=100)
    Tipo = models.CharField(max_length=100)
    Foto = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.Nombre


class Personajes(models.Model):
    Id = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=100)
    TipoDeMonstruo = models.CharField(max_length=100)
    FechaDeLanzamiento = models.CharField(max_length=7)
    FechaCumpleanios = models.CharField(max_length=5, null=True, blank=True)
    CiudadNatal = models.CharField(max_length=100, null=True, blank=True)
    Edad = models.IntegerField(null=True, blank=True)
    # Foto = models.ImageField(upload_to='personajes_fotos/', null=True, blank=True)
    MascotaId = models.ForeignKey('Mascotas', on_delete=models.SET_NULL, null=True, blank=True)
    EdicionesId = models.ManyToManyField('Ediciones', null=True, blank=True)
    Foto = models.JSONField(default=list, blank=True, null=True)
    Frase = models.TextField(null=True)
    ColorFav = models.TextField(null=True)
    Sexo = models.TextField(default='Femenino')

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(Sexo__in=["Masculino", "Femenino"]), name='chk_sexo')
        ]
    
    def __str__(self):
        return f"{self.Nombre} - Fotos: {self.Foto}"
    

class Ediciones(models.Model):
    Id = models.AutoField(primary_key=True)
    MunecaId = models.ManyToManyField('Personajes', blank=True)
    Serie = models.CharField(max_length=100)
    FechaDeLanzamiento = models.CharField(max_length=7)
    TipoDeGeneracion = models.PositiveSmallIntegerField()
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(TipoDeGeneracion__in=[1, 2, 3]), name='chk_tipo_generacion')
        ]
    
    def __str__(self):
        return f"{self.Serie} ({self.FechaDeLanzamiento}) - Fotos: {self.Foto}"

class Skullectors(models.Model):
    Id = models.AutoField(primary_key=True)
    MunecaId = models.ForeignKey('Personajes', on_delete=models.SET_NULL, null=True, blank=True)
    Serie = models.CharField(max_length=100)
    EdicionLimitada = models.BooleanField(default=False)
    Inspiracion = models.TextField(null=True)
    FechaDeLanzamiento = models.CharField(max_length=7)
    Descripcion = models.TextField()
    Foto = models.JSONField(default=list, null=True, blank=True)
    Certificado = models.BooleanField(default=False)
    PrecioOriginal = models.IntegerField(null=True)
    PrecioMercado = models.IntegerField(null=True)
    def __str__(self):
        return f"{self.Serie} ({self.FechaDeLanzamiento}) - Fotos: {self.Foto}"


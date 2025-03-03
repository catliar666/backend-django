from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.db import models
import re
from django.utils import timezone
from django.core import validators
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

# Create your models here.

class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError(_('The given username must be set'))
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password, True, True, **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user

class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _('username'),
        max_length=15,
        unique=True,
        help_text=_('Required. 15 characters or fewer. Letters, numbers and @/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(
                re.compile(r'^[\w.@+-]+$'),
                _('Enter a valid username.'),
                _('invalid')
            )
        ]
    )
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    
    # Sobrescribimos los campos heredados para evitar conflictos en las relaciones inversas.
    groups = models.ManyToManyField(
        Group,
        related_name='custom_users',  # O cualquier nombre único que no colisione
        blank=True,
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups')
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users_permissions',  # Nombre único para los permisos
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions')
    )
    
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    # Campos adicionales
    profile_picture = models.ImageField(
        _('profile picture'),
        upload_to='profile_images/',
        null=True,
        blank=True
    )
    description = models.TextField(_('description'), blank=True)
    gender = models.CharField(
        _('gender'),
        max_length=10,
        choices=[
            ('hombre', _('Hombre')),
            ('mujer', _('Mujer')),
            ('otro', _('Otro'))
        ],
        blank=True
    )
    pronouns = models.CharField(_('pronouns'), max_length=50, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])


class Personajes(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=True)
    monstruo = models.CharField(max_length=100, blank=True)
    lanzamiento = models.CharField(max_length=7)
    cumpleanios = models.CharField(max_length=5, null=True, blank=True)
    ciudadNatal = models.CharField(max_length=100, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    # mascota = models.ForeignKey('Mascotas', on_delete=models.SET_NULL, null=True, blank=True, related_name='mascota')
    # ediciones = models.ManyToManyField('Ediciones', blank=True, related_name='Personajes')
    # foto = models.ManyToManyField('Foto', blank=True, related_name='personajes')
    frase = models.TextField(null=True, blank=True)
    colorFav = models.TextField(null=True, blank=True)
    sexo = models.TextField(default='Femenino')
    fecha_subida = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(sexo__in=["Masculino", "Femenino"]), name='chk_sexo')
        ]
    
    def __str__(self):
        return self.nombre
    

class Mascotas(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    # foto = models.ManyToManyField('Foto', blank=True, related_name='mascotas')
    duenio = models.ForeignKey(Personajes, null=True, blank=False,  on_delete=models.CASCADE, related_name='mascota')
    fecha_subida = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True, auto_now=True)

    def __str__(self):
        return self.nombre


class Ediciones(models.Model):
    id = models.AutoField(primary_key=True)
    muneca = models.ForeignKey(Personajes, null=True, blank=True,  on_delete=models.CASCADE, related_name='ediciones')
    serie = models.CharField(max_length=100)
    lanzamiento = models.CharField(max_length=7)
    generacion = models.PositiveSmallIntegerField()
    # foto = models.ManyToManyField('Foto', blank=True, related_name='ediciones')
    fecha_subida = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True, auto_now=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(generacion__in=[1, 2, 3]), name='chk_generacion')
        ]
    
    def __str__(self):
        return f"{self.serie} ({self.lanzamiento}"

class Skullectors(models.Model):
    id = models.AutoField(primary_key=True)
    muneca = models.ForeignKey(Personajes, on_delete=models.CASCADE, null=True, blank=True, related_name='skullectors')
    serie = models.CharField(max_length=100)
    limitada = models.BooleanField(default=False)
    inspiracion = models.TextField(null=True)
    lanzamiento = models.CharField(max_length=7)
    descripcion = models.TextField()
    # foto = models.ManyToManyField('Foto', blank=True, related_name='skullectors')
    certificado = models.BooleanField(default=False)
    precioOriginal = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    precioMercado = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fecha_subida = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True, auto_now=True)
    def __str__(self):
        return f"{self.serie} ({self.lanzamiento}"
    

class Foto(models.Model):
    url = models.URLField(primary_key=True)
    munieca = models.ForeignKey(Personajes, null=True, blank=True, on_delete=models.CASCADE, related_name='fotos')
    edicion = models.ForeignKey(Ediciones, null=True, blank=True, on_delete=models.CASCADE, related_name='fotos')
    skullector = models.ForeignKey(Skullectors, null=True, blank=True, on_delete=models.CASCADE, related_name='fotos')
    mascota = models.ForeignKey(Mascotas, null=True, blank=True, on_delete=models.CASCADE, related_name='fotos')
    fecha_subida = models.DateTimeField(blank=False, default=timezone.now)
    def __str__(self):
        return self.url


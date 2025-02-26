from rest_framework import serializers
from .models import Personajes, Mascotas, Ediciones, Skullectors
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class MejoresAmigosSerializer(serializers.ModelSerializer):
    Nombre = serializers.CharField(required=True)
    class Meta:
        model = Personajes
        fields = ('Id', 'Nombre')

class PersonajesSerializer(serializers.ModelSerializer):
    Nombre = serializers.CharField(required=True)
    TipoDeMonstruo = serializers.CharField(required=True)
    FechaDeLanzamiento = serializers.CharField(required=True)
    FechaCumpleanios = serializers.CharField(required=False, allow_null=True)
    Edad = serializers.IntegerField(required=True)
    CiudadNatal = serializers.CharField(required=False, allow_null=True)
    Foto = serializers.JSONField(default=list, required=False, allow_null=True)
    Frase = serializers.CharField(required=False)
    ColorFav = serializers.CharField(required=False)
    Sexo = serializers.CharField(required=True)
    class Meta:
        model = Personajes
        fields = ('Id', 'Nombre', 'TipoDeMonstruo', 'FechaDeLanzamiento', 'FechaCumpleanios', 'CiudadNatal', 'Edad', 'Foto', 'Frase', 'ColorFav', 'Sexo')

class MascotasSerializer(serializers.ModelSerializer):
    Nombre = serializers.CharField(required=True)
    Tipo = serializers.CharField(required=True)
    Foto = serializers.URLField(required=False, allow_null=True)
    class Meta:
        model = Mascotas
        fields = ('Id', 'Nombre', 'Tipo', 'Foto')


class SkullectorSerializer(serializers.ModelSerializer):
    Serie = serializers.CharField(required=True)
    FechaDeLanzamiento = serializers.CharField(required=True)
    Foto = serializers.URLField(required=False, allow_null=True)
    Descripcion = serializers.CharField(required=True)
    MunecaId = PersonajesSerializer(required=False)
    EdicionLimitada = serializers.BooleanField(required=True)
    Inspiracion = serializers.CharField(required=False)
    Certificado = serializers.BooleanField(required=True)
    PrecioOriginal = serializers.IntegerField(required=False,default=0)
    PrecioMercado = serializers.IntegerField(required=False,default=0)
    class Meta:
        model = Skullectors
        fields = ('Id', 'Serie', 'FechaDeLanzamiento', 'Descripcion', 'Foto', 'EdicionLimitada', 'Inspiracion', 'Certificado', 'PrecioOriginal', 'PrecioMercado', 'MunecaId')


class EdicionesSerializer(serializers.ModelSerializer):
    Serie = serializers.CharField(required=True)
    FechaDeLanzamiento = serializers.CharField(required=True)
    TipoDeGeneracion = serializers.CharField(required=True)
    class Meta:
        model = Ediciones
        fields = ('Id', 'Serie', 'FechaDeLanzamiento', 'TipoDeGeneracion')

class CompletoSerializer(serializers.ModelSerializer):
    EdicionesId = EdicionesSerializer(many=True)
    MascotaId = MascotasSerializer()
    class Meta:
        model = Personajes
        fields = ('Id', 'Nombre', 'TipoDeMonstruo', 'FechaDeLanzamiento', 'FechaCumpleanios', 'CiudadNatal', 'Edad', 'Foto', 'Frase', 'ColorFav', 'Sexo', 'MascotaId', 'EdicionesId')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        refresh = RefreshToken.for_user(user)
        return {
            'user': UserSerializer(user).data,  
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    def create_superuser(request):
        data = request.data

        if User.objects.filter(username=data["username"]).exists():
            return {"error": "El usuario ya existe"}

        # Crear el superusuario
        user = User.objects.create_superuser(
            username=data["username"],
            email=data["email"],
            password=data["password"]
        )
        refresh = RefreshToken.for_user(user)

        return {
            'user': UserSerializer(user).data,  
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': "Superusuario creado correctamente"
        }



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Credenciales incorrectas")
        
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }


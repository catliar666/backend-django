from rest_framework import serializers
from .models import Personajes, Mascotas, Ediciones, Skullectors, Foto, Usuario
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

# Usuario = get_user_model()

class FotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foto
        fields = ['url']

class MascotasSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=True)
    tipo = serializers.CharField(required=True)
    fotos = FotoSerializer(many=True, read_only=True)
    class Meta:
        model = Mascotas
        fields = ('id', 'nombre', 'tipo', 'fotos')



class PersonajesSerializer(serializers.ModelSerializer):
    fotos = FotoSerializer(many=True, read_only=True)
    nombre = serializers.CharField(required=True)
    monstruo = serializers.CharField(required=True)
    lanzamiento = serializers.CharField(required=True)
    cumpleanios = serializers.CharField(required=False, allow_null=True)
    edad = serializers.IntegerField(required=True)
    ciudadNatal = serializers.CharField(required=False, allow_null=True)
    frase = serializers.CharField(required=False)
    colorFav = serializers.CharField(required=False)
    sexo = serializers.CharField(required=True)


    class Meta:
        model = Personajes
        fields = ('id', 'nombre', 'monstruo', 'lanzamiento', 'cumpleanios', 'ciudadNatal', 'edad', 'fotos', 'frase', 'colorFav', 'sexo')

class MascotasCompletaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(required=True)
    tipo = serializers.CharField(required=True)
    fotos = FotoSerializer(many=True, read_only=True)
    duenio = PersonajesSerializer()
    class Meta:
        model = Mascotas
        fields = ('id', 'nombre', 'tipo', 'fotos', 'duenio')

class SkullectorSerializer(serializers.ModelSerializer):
    serie = serializers.CharField(required=True)
    lanzamiento = serializers.CharField(required=True)
    fotos = FotoSerializer(many=True, read_only=True)
    descripcion = serializers.CharField(required=True)
    limitada = serializers.BooleanField(required=True)
    inspiracion = serializers.CharField(required=False)
    certificado = serializers.BooleanField(required=True)
    precioOriginal = serializers.IntegerField(required=False,default=0)
    precioMercado = serializers.IntegerField(required=False,default=0)
    class Meta:
        model = Skullectors
        fields = ('id', 'serie', 'lanzamiento', 'descripcion', 'fotos', 'limitada', 'inspiracion', 'certificado', 'precioOriginal', 'precioMercado', 'muneca')


class SkullectorCompletaSerializer(serializers.ModelSerializer):
    serie = serializers.CharField(required=True)
    lanzamiento = serializers.CharField(required=True)
    fotos = FotoSerializer(many=True, read_only=True)
    descripcion = serializers.CharField(required=True)
    muneca = PersonajesSerializer(required=False)
    limitada = serializers.BooleanField(required=True)
    inspiracion = serializers.CharField(required=False)
    certificado = serializers.BooleanField(required=True)
    precioOriginal = serializers.IntegerField(required=False,default=0)
    precioMercado = serializers.IntegerField(required=False,default=0)
    class Meta:
        model = Skullectors
        fields = ('id', 'serie', 'lanzamiento', 'descripcion', 'fotos', 'limitada', 'inspiracion', 'certificado', 'precioOriginal', 'precioMercado', 'muneca')


class EdicionCompletaSerializer(serializers.ModelSerializer):
    serie = serializers.CharField(required=True)
    lanzamiento = serializers.CharField(required=True)
    generacion = serializers.CharField(required=True)
    fotos = FotoSerializer(many=True, read_only=True)
    muneca = PersonajesSerializer()
    class Meta:
        model = Ediciones
        fields = ('id', 'serie', 'lanzamiento', 'generacion', 'fotos', 'muneca')

class EdicionesSerializer(serializers.ModelSerializer):
    serie = serializers.CharField(required=True)
    lanzamiento = serializers.CharField(required=True)
    generacion = serializers.CharField(required=True)
    fotos = FotoSerializer(many=True, read_only=True)
    class Meta:
        model = Ediciones
        fields = ('id', 'serie', 'lanzamiento', 'generacion', 'fotos')

class CompletoSerializer(serializers.ModelSerializer):
    ediciones = EdicionesSerializer(required=False, allow_null=True, many=True)
    skullectors = SkullectorSerializer(required=False, allow_null=True, many=True)
    mascota = MascotasSerializer(required=False, allow_null=True, many=True)
    fotos = FotoSerializer(many=True, read_only=True)
    class Meta:
        model = Personajes
        fields = ('id', 'nombre', 'monstruo', 'lanzamiento', 'cumpleanios', 'ciudadNatal', 'edad', 'fotos', 'frase', 'colorFav', 'sexo', 'mascota', 'ediciones', 'skullectors')



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id','username','email','first_name','last_name','profile_picture','description','gender','pronouns','is_staff',]



class RegisterSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=[('hombre', 'Hombre'), ('mujer', 'Mujer'), ('otro', 'Otro')],
        required=False,
        allow_blank=True
    )
    pronouns = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'password',
            'profile_picture',
            'description',
            'gender',
            'pronouns'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        description = validated_data.pop('description', '')
        gender = validated_data.pop('gender', '')
        pronouns = validated_data.pop('pronouns', '')

        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile_picture=profile_picture,
            description=description,
            gender=gender,
            pronouns=pronouns
        )
        refresh = RefreshToken.for_user(user)
        return {
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message':'Usuario creado correctamente'
        }
    def create_superuser(request):
        data = request.data

        if Usuario.objects.filter(username=data["username"]).exists():
            return {"error": "El usuario ya existe"}

        user = Usuario.objects.create_superuser(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            profile_picture=data.get("profile_picture", None),
            description=data.get("description", ""),
            gender=data.get("gender", ""),
            pronouns=data.get("pronouns", "")
        )
        refresh = RefreshToken.for_user(user)

        return {
            'user': UserSerializer(user).data,  
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': "Superusuario creado correctamente"
        }



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("El email y la contraseña son obligatorios")
        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError("Credenciales incorrectas")
        
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }


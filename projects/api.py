from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from .models import Personajes, Mascotas, Ediciones, Skullectors, Usuario
from rest_framework import viewsets, filters, status, permissions
from .permisions import IsAdminOrReadOnly
from .serializers import PersonajesSerializer, MascotasCompletaSerializer, CompletoSerializer, EdicionCompletaSerializer, UserSerializer, SkullectorCompletaSerializer, RegisterSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.filters import OrderingFilter
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, ParseError


class CompletoViewSet(viewsets.ModelViewSet):
    queryset = Personajes.objects.all()
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    serializer_class = CompletoSerializer

    filter_backends = [filters.SearchFilter, OrderingFilter]
    ordering_fields = '__all__'
    search_fields = ('nombre', 'generacion', 'edad', 'lanzamiento', 'cumpleanios', 'tipoMascota', 'tipo', 'ciudad', 'frase', 'colorFav', 'sexo', 'ordering')


    def get_queryset(self):
        queryset = Personajes.objects.all()
        params = self.request.query_params

        generacion = params.get('generacion', None)
        if generacion is not None:
            try:
                generacion = int(generacion)
                queryset = queryset.filter(ediciones__generacion=generacion).distinct()
            except ValueError:
                raise ValidationError("El parámetro 'generacion' debe ser un número")

        nombre = params.get('nombre', None)
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)

        edad = params.get('edad', None)
        if edad is not None:
            queryset = queryset.filter(edad=edad)

        fechaLanzamiento = params.get('lanzamiento', None)
        if fechaLanzamiento is not None:
            queryset = queryset.filter(lanzamiento__icontains=fechaLanzamiento)

        fechaCumpleanios = params.get('cumpleanios', None)
        if fechaCumpleanios is not None:
            queryset = queryset.filter(cumpleanios__icontains=fechaCumpleanios)

        tipoMascota = params.get('tipoMascota', None)
        if tipoMascota is not None:
            queryset = queryset.filter(mascota__Tipo=tipoMascota)

        tipo = params.get('tipo', None)
        if tipo is not None:
            queryset = queryset.filter(monstruo__icontains=tipo)

        ciudad = params.get('ciudad', None)
        if ciudad is not None:
            queryset = queryset.filter(ciudadNatal__icontains=ciudad)

        frase = params.get('frase', None)
        if frase is not None:
            queryset = queryset.filter(frase__icontains=frase)

        colorFav = params.get('colorFav', None)
        if colorFav is not None:
            queryset = queryset.filter(colorFav__icontains=colorFav)

        sexo = params.get('sexo', None)
        if sexo is not None:
            queryset = queryset.filter(sexo__icontains=sexo)

        ordering = params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(*ordering.split(','))


        return queryset
    


    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            return super().list(request, *args, **kwargs)

        except ValidationError as e:
            return Response({"error": "Error de validación en los datos enviados", "detalles": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({"error": "El recurso solicitado no existe"}, status=status.HTTP_404_NOT_FOUND)

        except NotAuthenticated:
            return Response({"error": "No estás autenticado para acceder a este recurso"}, status=status.HTTP_401_UNAUTHORIZED)

        except PermissionDenied:
            return Response({"error": "No tienes permiso para realizar esta acción"}, status=status.HTTP_403_FORBIDDEN)

        except ParseError:
            return Response({"error": "Error en el formato de la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except TypeError:
            return Response({"error": "Error de tipo de dato en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except KeyError:
            return Response({"error": "Faltan datos obligatorios en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "Error inesperado, contacte con el administrador.", "detalles": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class EdicionesViewSet(viewsets.ModelViewSet):
    queryset = Ediciones.objects.all()
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    serializer_class = EdicionCompletaSerializer

    filter_backends = [filters.SearchFilter, OrderingFilter]
    ordering_fields = '__all__'
    search_fields = ('serie', 'generacion', 'lanzamiento', 'precio', 'ordering')

    def update(self, request, pk=None):
        try:
            edicion = get_object_or_404(Ediciones, id=pk)
            serializer = self.get_serializer(edicion, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None):
        try:
            edicion = get_object_or_404(Ediciones, id=pk)
            serializer = self.get_serializer(edicion, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def destroy(self, request, pk=None):
        try:
            edicion = get_object_or_404(Ediciones, id=pk)
            if hasattr(edicion, 'EdicionesId') and edicion.MunecaId is not None:
                edicion.MuniecaId.clear()

            edicion.delete()

            return Response({"message": f"Edicion con ID {pk} eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Ediciones.DoesNotExist:
            return Response({"error": "La edición introducida no existe"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_destroy(self, instance):
        instance.delete()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {"error": "Datos inválidos", "detalles": e.detail},  
                status=status.HTTP_400_BAD_REQUEST
            )
        except DjangoValidationError as e:  
            return Response(
                {"error": "Error de validación en el modelo", "detalles": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except TypeError as e:
            return Response(
                {"error": "Error de tipo en los datos proporcionados", "detalles": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Error inesperado, contacte con el administrador", "detalles": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        queryset = Ediciones.objects.all()
        params = self.request.query_params

        #Busca por generacion
        generacion = params.get('generacion', None)
        if generacion is not None:
            queryset = queryset.filter(generacion=generacion)
        #Busca por coincidencia en serie
        serie = params.get('serie', None)
        if serie is not None:
            queryset = queryset.filter(serie__icontains=serie)
        lanzamiento = params.get('lanzamiento', None)
        if lanzamiento is not None:
            queryset = queryset.filter(lanzamiento__icontains=lanzamiento)
        precio = params.get('precio', None)
        if precio is not None:
            queryset = queryset.filter(precio__icontains=precio)
        ordering = params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(*ordering.split(','))

        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            return super().list(request, *args, **kwargs)

        except ValidationError as e:
            return Response({"error": "Error de validación en los datos enviados", "detalles": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({"error": "El recurso solicitado no existe"}, status=status.HTTP_404_NOT_FOUND)

        except NotAuthenticated:
            return Response({"error": "No estás autenticado para acceder a este recurso"}, status=status.HTTP_401_UNAUTHORIZED)

        except PermissionDenied:
            return Response({"error": "No tienes permiso para realizar esta acción"}, status=status.HTTP_403_FORBIDDEN)

        except ParseError:
            return Response({"error": "Error en el formato de la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except TypeError:
            return Response({"error": "Error de tipo de dato en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except KeyError:
            return Response({"error": "Faltan datos obligatorios en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "Error inesperado, contacte con el administrador.", "detalles": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class SkullectorViewSet(viewsets.ModelViewSet):
    queryset = Skullectors.objects.all()
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    serializer_class = SkullectorCompletaSerializer


    filter_backends = [filters.SearchFilter, OrderingFilter]
    ordering_fields = '__all__'
    search_fields = ('serie', 'descripcion', 'lanzamiento', 'edicionLimitada', 'inspiracion', 'certificado', 'precioOriginal', 'precioMercado', 'ordering')
    def create(self, request, *args, **kwargs):
        try:
            serie = request.data.get("serie")
            descripcion = request.data.get("descripcion")
            fechaLanzamiento = request.data.get("lanzamiento")
            foto = request.data.get("foto")
            if (Skullectors.objects.filter(serie=serie, descripcion=descripcion, lanzamiento=fechaLanzamiento).exists()):
                return Response({"error":"Esta skullector ya existe"}, status=status.HTTP_409_CONFLICT)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {"error": "Datos inválidos", "detalles": e.detail},  
                status=status.HTTP_400_BAD_REQUEST
            )
        except DjangoValidationError as e:  
            return Response(
                {"error": "Error de validación en el modelo", "detalles": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except TypeError as e:
            return Response(
                {"error": "Error de tipo en los datos proporcionados", "detalles": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Error inesperado, contacte con el administrador", "detalles": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, pk=None):
        try:
            personaje = get_object_or_404(Personajes, id=pk)
            serializer = self.get_serializer(personaje, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None):
        try:
            personaje = get_object_or_404(Personajes, id=pk)
            serializer = self.get_serializer(personaje, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            skullector = get_object_or_404(Skullectors, id=pk)
            if hasattr(skullector, 'muneca') and skullector.muneca is not None:
                skullector.muneca.clear()
            skullector.delete()

            return Response({"message": f"Skullector con ID {pk} eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Skullectors.DoesNotExist:
            return Response({"error": "Esta Skullector no existe"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_destroy(self, instance):
        instance.delete()



    def get_queryset(self):
        queryset = Skullectors.objects.all()
        params = self.request.query_params

        #Busca por descripcion
        descripcion = params.get('descripcion', None)
        if descripcion is not None:
            queryset = queryset.filter(descripcion__icontains=descripcion)
        #Busca por coincidencia en serie
        serie = params.get('serie', None)
        if serie is not None:
            queryset = queryset.filter(serie__icontains=serie)

        lanzamiento = params.get('lanzamiento', None)
        if lanzamiento is not None:
            queryset = queryset.filter(lanzamiento__icontains=lanzamiento)

        edicionLimitada = params.get('edicionLimitada', None)
        if edicionLimitada is not None:
            queryset = queryset.filter(limitada=edicionLimitada)

        certificado = params.get('certificado', None)
        if certificado is not None:
            queryset = queryset.filter(certificado=certificado)

        precioOriginal = params.get('precioOriginal', None)
        if precioOriginal is not None:
            queryset = queryset.filter(precioOriginal__icontains=precioOriginal)

        precioMercado = params.get('precioMercado', None)
        if precioMercado is not None:
            queryset = queryset.filter(precioMercado__icontains=precioMercado)

        inspiracion = params.get('inspiracion', None)
        if inspiracion is not None:
            queryset = queryset.filter(inspiracion__icontains=inspiracion)
        
        ordering = params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(*ordering.split(','))
        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            return super().list(request, *args, **kwargs)

        except ValidationError as e:
            return Response({"error": "Error de validación en los datos enviados", "detalles": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({"error": "El recurso solicitado no existe"}, status=status.HTTP_404_NOT_FOUND)

        except NotAuthenticated:
            return Response({"error": "No estás autenticado para acceder a este recurso"}, status=status.HTTP_401_UNAUTHORIZED)

        except PermissionDenied:
            return Response({"error": "No tienes permiso para realizar esta acción"}, status=status.HTTP_403_FORBIDDEN)

        except ParseError:
            return Response({"error": "Error en el formato de la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except TypeError:
            return Response({"error": "Error de tipo de dato en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except KeyError:
            return Response({"error": "Faltan datos obligatorios en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "Error inesperado, contacte con el administrador.", "detalles": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    



class PersonajesViewSet(viewsets.ModelViewSet):
    queryset = Personajes.objects.all()
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    serializer_class = PersonajesSerializer

    filter_backends = [filters.SearchFilter, OrderingFilter]
    ordering_fields = '__all__'
    search_fields = ('nombre', 'monstruo', 'ciudad', 'edad', 'lanzamiento', 'fechaCumpleanios', 'frase', 'colorFav', 'sexo', 'ordering')

    def create(self, request, *args, **kwargs):
        try:
            nombre = request.data.get("nombre")
            tipo = request.data.get("monstruo")
            fecha_lanzamiento = request.data.get("lanzamiento")
            edad = request.data.get("edad")
            mascota_id = request.data.get("mascota")
            ediciones_ids = request.data.get("ediciones", [])
            foto = request.data.get("foto")
            frase = request.data.get("frase")
            color_fav = request.data.get("colorFav")
            sexo = request.data.get("sexo", "Femenino")

            if Personajes.objects.filter(
                nombre=nombre,
                monstruo=tipo,
                lanzamiento=fecha_lanzamiento,
                edad=edad,
                sexo=sexo
            ).exists():
                return Response(
                    {"error": "Este personaje ya existe"},
                    status=status.HTTP_409_CONFLICT
                )
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            personaje = serializer.save()
            if mascota_id:
                personaje.mascota_id = mascota_id
                personaje.save()
            if ediciones_ids:
                personaje.ediciones.set(ediciones_ids)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {"error": "Datos inválidos", "detalles": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DjangoValidationError as e: 
            return Response(
                {"error": "Error de validación", "detalles": e.message_dict}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "Error inesperado, contacte con el administrador"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        try:
            personaje = get_object_or_404(Personajes, id=pk)
            serializer = self.get_serializer(personaje, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None):
        try:
            personaje = get_object_or_404(Personajes, id=pk)
            serializer = self.get_serializer(personaje, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def destroy(self, request, pk=None):
        try:
            personaje = get_object_or_404(Personajes, id=pk)
            personaje.delete()

            return Response({"message": f"Personaje con ID {pk} eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Personajes.DoesNotExist:
            return Response({"error": "El personaje no existe"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_destroy(self, instance):
        instance.delete()

    def get_queryset(self):
        queryset = Personajes.objects.all()
        params = self.request.query_params

        #Busca por generacion
        nombre = params.get('nombre', None)
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)

        tipo = params.get('tipo', None)
        if tipo is not None:
            queryset = queryset.filter(monstruo__icontains=tipo)

        ciudad = params.get('ciudad', None)
        if ciudad is not None:
            queryset = queryset.filter(ciudadNatal__icontains=ciudad) 

        edad = params.get('edad', None)
        if edad is not None:
            try:
                edad = int(edad)
                queryset = queryset.filter(edad=edad)
            except ValueError:
                ValidationError("La edad debe ser un número")

        lanzamiento = params.get('lanzamiento', None)
        if lanzamiento is not None:
            queryset = queryset.filter(lanzamiento__icontains=lanzamiento)

        fechaCumpleanios = params.get('cumpleanios', None)
        if fechaCumpleanios is not None:
            queryset = queryset.filter(cumpleanios__icontains=fechaCumpleanios)

        frase = params.get('frase', None)
        if frase is not None:
            queryset = queryset.filter(frase__icontains=frase)

        colorFav = params.get('colorFav', None)
        if colorFav is not None:
            queryset = queryset.filter(colorFav__icontains=colorFav)
        
        sexo = params.get('sexo', None)
        if sexo is not None:
            queryset = queryset.filter(sexo=sexo)

        ordering = params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(*ordering.split(','))

        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            return super().list(request, *args, **kwargs)

        except ValidationError as e:
            return Response({"error": "Error de validación en los datos enviados", "detalles": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({"error": "El recurso solicitado no existe"}, status=status.HTTP_404_NOT_FOUND)

        except NotAuthenticated:
            return Response({"error": "No estás autenticado para acceder a este recurso"}, status=status.HTTP_401_UNAUTHORIZED)

        except PermissionDenied:
            return Response({"error": "No tienes permiso para realizar esta acción"}, status=status.HTTP_403_FORBIDDEN)

        except ParseError:
            return Response({"error": "Error en el formato de la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except TypeError:
            return Response({"error": "Error de tipo de dato en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except KeyError:
            return Response({"error": "Faltan datos obligatorios en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "Error inesperado, contacte con el administrador.", "detalles": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MascotasViewSet(viewsets.ModelViewSet):
    queryset = Mascotas.objects.all()
    permission_classes = [IsAdminOrReadOnly, IsAuthenticated]
    serializer_class = MascotasCompletaSerializer

    filter_backends = [filters.SearchFilter, OrderingFilter]
    ordering_fields = '__all__'
    search_fields = ('nombre', 'tipo', 'ordering')

    def get_queryset(self):
        queryset = Mascotas.objects.all()
        params = self.request.query_params

        #Busca por generacion
        nombre = params.get('nombre', None)
        if nombre is not None:
            queryset = queryset.filter(nombre__icontains=nombre)
        #Busca por coincidencia en serie
        tipo = params.get('tipo', None)
        if tipo is not None:
            queryset = queryset.filter(tipo__icontains=tipo)

        ordering = params.get('ordering', None)
        if ordering:
            queryset = queryset.order_by(*ordering.split(','))
        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            return super().list(request, *args, **kwargs)

        except ValidationError as e:
            return Response({"error": "Error de validación en los datos enviados", "detalles": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({"error": "El recurso solicitado no existe"}, status=status.HTTP_404_NOT_FOUND)

        except NotAuthenticated:
            return Response({"error": "No estás autenticado para acceder a este recurso"}, status=status.HTTP_401_UNAUTHORIZED)

        except PermissionDenied:
            return Response({"error": "No tienes permiso para realizar esta acción"}, status=status.HTTP_403_FORBIDDEN)

        except ParseError:
            return Response({"error": "Error en el formato de la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except TypeError:
            return Response({"error": "Error de tipo de dato en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except KeyError:
            return Response({"error": "Faltan datos obligatorios en la solicitud"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": "Error inesperado, contacte con el administrador.", "detalles": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        try:
            # fields = ('Id', 'Nombre', 'Tipo', 'Foto')
            nombre = request.data.get("nombre")
            tipo = request.data.get("tipo")
            if (Mascotas.objects.filter(nombre=nombre, tipo=tipo).exists()):
                return Response({"error":"Esta mascota ya existe"}, status=status.HTTP_409_CONFLICT)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": "Datos inválidos", "detalles": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Error inesperado"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, pk=None):
        try:
            mascotas = get_object_or_404(Mascotas, Id=pk)
            serializer = self.get_serializer(mascotas, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            mascota = get_object_or_404(Mascotas, Id=pk)
            mascota.delete()
            return Response({"message": f"Mascota con ID {pk} eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)
        except Personajes.DoesNotExist:
            return Response({"error": "La mascota no existe"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_destroy(self, instance):
        instance.delete()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.save(), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Sirve para iniciar sesión con un usuario y que le cree los token válidos
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

#Se utiliza para cerrar la sesion de un usuario e invalidar los token que tiene activos
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Sesión cerrada correctamente"}, status=200)
        except Exception:
            return Response({"error": "Token inválido o ya expirado"}, status=400)

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UserSerializer

    # La acción partial_update (PATCH) ya está implementada por defecto,
    # por lo que no necesitas sobrescribirla a menos que requieras lógica adicional.

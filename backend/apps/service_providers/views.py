from django.contrib.gis.geos import Point  # ,GEOSGeometry
from django.contrib.gis.measure import D
from rest_framework import generics, status, viewsets
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# from math import sin, cos, sqrt, atan2, radians
from .models import *
from .permissions import IsServiceProvider
from .serializers import *


class LocationView(APIView):
    """Get Location if exists else create a new one"""

    permission_classes = [IsAuthenticated]
    serializer_class = LocationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            lat = serializer.initial_data["lat"]
            lon = serializer.initial_data["lon"]
            location = Location.objects.get(lat=lat, lon=lon)
            serializer = self.serializer_class(location)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Location.DoesNotExist:
            if serializer.is_valid():
                serializer.save()
                location_point = Location.objects.get(id=serializer.data["id"])
                location_point.point = Point(
                    serializer.data["lon"], serializer.data["lat"]
                )
                location_point.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MoversViewset(viewsets.ModelViewSet):

    """
    This viewset is used by authenticated user only
    user can crete update and delete its Movers
    """

    permission_classes = [IsServiceProvider]
    queryset = Movers.objects.all()
    serializer_class = MoverSerializer
    http_method_names = ["get", "post", "head", "patch"]

    def get_queryset(self):
        """
        This function is used to set user of the Movers
        """
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class OrganizersViewset(viewsets.ModelViewSet):

    """
    This viewset is used by authenticated user only
    user can crete update and delete its Organizers
    """

    permission_classes = [IsServiceProvider]
    queryset = Organizers.objects.all()
    serializer_class = OrganizerSerializer
    http_method_names = ["get", "post", "head", "patch"]

    def get_queryset(self):
        """
        This function is used to set user of the Organizers
        """
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class StorageUnitProviderViewset(viewsets.ModelViewSet):
    permission_classes = [IsServiceProvider]
    queryset = StorageUnitProvider.objects.all()
    serializer_class = StorageUnitProviderSerializer
    http_method_names = ["get", "post", "head", "patch"]

    def get_queryset(self):
        """
        This function is used to set user of the Organizers
        """
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class MoversView(generics.ListAPIView):

    """Filter Movers and list them"""

    serializer_class = MoverSerializer
    permission_classes = [AllowAny]
    queryset = Movers.objects.all()


class OrganizersView(generics.ListAPIView):

    """Filter Organizers and list them"""

    serializer_class = OrganizerSerializer
    permission_classes = [AllowAny]
    queryset = Organizers.objects.all()


class DetailMoversView(generics.GenericAPIView, RetrieveModelMixin):

    """Filter Movers and list them"""

    serializer_class = MoverSerializer
    permission_classes = [AllowAny]
    queryset = Movers.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DetailOrganizersView(generics.GenericAPIView, RetrieveModelMixin):

    """Filter Organizers and list them"""

    serializer_class = OrganizerSerializer
    permission_classes = [AllowAny]
    queryset = Organizers.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

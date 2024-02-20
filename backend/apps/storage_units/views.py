from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets, views
from rest_framework.mixins import (
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.service_providers.permissions import IsServiceProvider

from .models import *
from .serializers import *


# Create your views here.
class StorageFacilityViewset(viewsets.ModelViewSet):
    """
    This view will create, update, get and
    delete Storage Facility
    """

    permission_classes = [IsServiceProvider]
    queryset = StorageFacility.objects.all()
    serializer_class = StorageFacilitySerializer

    def get_queryset(self):
        """
        This function is used to set user of the Organizers
        """
        queryset = self.queryset
        query_set = queryset.filter(storage_provider__user=self.request.user)
        return query_set


class StorageUnitView(generics.ListCreateAPIView):
    """
    Get all rooms and post a new room this is only
    for service provider admin
    """

    permission_classes = [IsServiceProvider]
    queryset = StorageUnit.objects.all()
    serializer_class = StorageUnitSerializer

    def get_queryset(self, *args, **kwargs):
        facility_id = self.kwargs["facility_id"]
        storage_unit = self.queryset.filter(storage_facility__id=facility_id)
        return storage_unit

    def post(self, request, facility_id):
        is_many = isinstance(request.data, list)
        if not is_many:
            serializer = self.serializer_class(data=request.data)
            try:
                storage_facility_ids = StorageFacility.objects.get(id=facility_id)

            except StorageFacility.DoesNotExist:
                return Response(
                    {"error": "storage not found"}, status=status.HTTP_404_NOT_FOUND
                )

            if serializer.is_valid():
                serializer.save(storage_facility_ids=storage_facility_ids)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            serializer = self.serializer_class(data=request.data, many=True)
            try:
                storage_facility_ids = StorageFacility.objects.get(id=facility_id)

            except StorageFacility.DoesNotExist:
                return Response(
                    {"error": "storage not found"}, status=status.HTTP_404_NOT_FOUND
                )

            if serializer.is_valid():
                serializer.save(storage_facility_ids=storage_facility_ids)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StorageUnitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get specific, update, delete a room this is only
    for service provider admin
    """

    permission_classes = [IsServiceProvider]
    queryset = StorageUnit.objects.all()
    serializer_class = StorageUnitSerializer

    def get(self, request, storage_id):
        try:
            storage_unit = StorageUnit.objects.get(id=storage_id)
            serializer = self.serializer_class(storage_unit)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except StorageUnit.DoesNotExist:
            return Response(
                {"error": "storage unit not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request, storage_id):
        try:
            storage_unit = StorageUnit.objects.get(id=storage_id)

        except StorageUnit.DoesNotExist:
            return Response(
                {"error": "storage unit not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            storage_facility_ids = StorageFacility.objects.get(
                id=storage_unit.storage_facility.id
            )

        except StorageFacility.DoesNotExist:
            return Response(
                {"error": "storage not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(
            storage_unit, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save(storage_facility_ids=storage_facility_ids)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, storage_id):
        try:
            storage_unit = StorageUnit.objects.get(id=storage_id)
            storage_facility = StorageFacility.objects.get(
                id=storage_unit.storage_facility.id
            )
            storage_facility.total_size -= storage_unit.size
            if storage_facility.free_space == 0:
                storage_facility.free_space = 0
            else:
                storage_facility.free_space -= storage_unit.size

            if storage_facility.occupied_space is None:
                storage_facility.occupied_space = 0
            else:
                if storage_facility.occupied_space == 0:
                    storage_facility.occupied_space = 0
                else:
                    storage_facility.occupied_space -= storage_unit.size

            if storage_facility.total_storage_units == 0:
                storage_facility.total_storage_units = 0
            else:
                storage_facility.total_storage_units -= 1

            if storage_facility.available_storage_units == 0:
                storage_facility.available_storage_units = 0
            else:
                storage_facility.available_storage_units -= 1

            if storage_facility.occupied_storage_unit is None:
                storage_facility.occupied_storage_unit = 0
            else:
                if storage_facility.occupied_storage_unit == 0:
                    storage_facility.occupied_storage_unit = 0
                else:
                    storage_facility.occupied_storage_unit -= 1
            minimum = StorageUnit.objects.filter(
                storage_facility__id=storage_facility.id
            ).aggregate(Min("per_unit_price"))["per_unit_price__min"]
            storage_facility.minimum_price = minimum

            storage_facility.save()
            storage_unit.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except StorageFacility.DoesNotExist:
            return Response(
                {"error": "storage not found"}, status=status.HTTP_404_NOT_FOUND
            )


class DistinctStorageUnit(views.APIView):
    """
    This view will show admin user distinct storage units
    he/she has
    """

    permission_classes = [IsServiceProvider]
    serializer_class = GetStorageUnitSerializer

    def get(self, request):
        query = StorageUnit.objects.filter(
            storage_facility__storage_provider__user=self.request.user
        ).distinct("name")
        serializer = self.serializer_class(query, many=True)
        return Response(serializer.data)


class DistinctStorageFacility(views.APIView):
    """
    This view will show admin user distinct storage Facility
    he/she has
    """

    permission_classes = [IsServiceProvider]
    serializer_class = GetStorageFacilitySerializer

    def get(self, request):
        query = StorageFacility.objects.filter(
            storage_provider__user=self.request.user
        ).distinct("name")
        serializer = self.serializer_class(query, many=True)
        return Response(serializer.data)


class TotalStorageUnit(generics.ListAPIView):
    """
    This view will show admin user total storage units
    he/she has
    """

    permission_classes = [IsServiceProvider]
    queryset = StorageUnit.objects.all()
    serializer_class = StorageUnitSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = ["is_available", "storage_facility__name", "name"]
    search_fields = ["name", "storage_facility__name", "storage_facility__location__address"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(
            storage_facility__storage_provider__user=self.request.user
        )
        return query_set


class AvailableStorageUnit(generics.ListAPIView):
    """
    This view will show available storage units
    a user has
    """

    permission_classes = [IsServiceProvider]
    queryset = StorageUnit.objects.all()
    serializer_class = StorageUnitSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        "is_available",
        "is_occupied",
    ]
    search_fields = ["name", "storage_facility__name"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(
            storage_facility__storage_provider__user=self.request.user,
            is_available=True,
        )
        return query_set


class OccupiedStorageUnit(generics.ListAPIView):
    """
    This view will show occupied storage units
    a user has
    """

    permission_classes = [IsServiceProvider]
    queryset = StorageUnit.objects.all()
    serializer_class = StorageUnitSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        "is_available",
        "is_occupied",
    ]
    search_fields = ["name", "storage_facility__name"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(
            storage_facility__storage_provider__user=self.request.user, is_occupied=True
        )
        return query_set


class PostRatingsView(generics.CreateAPIView):
    """
    This view will post ratings for a
    storage facility.
    """

    permission_classes = [IsAuthenticated]
    queryset = Ratings.objects.all()
    serializer_class = RatingsSerializer

    def post(self, request, facility_id):
        try:
            facility = StorageFacility.objects.get(id=facility_id)
            serializer = self.serializer_class(
                data=request.data,
                context={"user": self.request.user, "storage_facility": facility},
            )
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(
                {"msg": "the facility id does not exits"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RandomStorageFacilityView(generics.ListAPIView):
    """
    Filter StorageUnit and list them
    """

    serializer_class = StorageFacilitySerializer
    permission_classes = [AllowAny]
    queryset = StorageFacility.objects.all().order_by("-id")[:5]


class FilterPagination(PageNumberPagination):
    """
    Custom pagination for a view
    """

    page_size = 10


class StorageFacilitySearchView(generics.ListAPIView):
    """
    Filter StorageUnit and list them
    """

    serializer_class = SearchStorageFacilitesSerialzier
    permission_classes = [AllowAny]
    queryset = StorageFacility.objects.all()
    pagination_class = FilterPagination

    def list(self, request):
        location = request.query_params.get("location", None)
        size = request.query_params.get("size", None)
        small_size = request.query_params.get("small_size", None)
        medium_size = request.query_params.get("medium_size", None)
        large_size = request.query_params.get("large_size", None)
        storage_type = request.query_params.get("storage_type", None)
        small = 100
        large = 10000
        medium = 3600

        if location and size and storage_type:
            query = self.queryset.filter(
                free_space__gte=size,
                location__address__icontains=location,
                storage_unit__storage_unit_type__in=storage_type.split(),
                storage_unit__is_available=True,
            ).distinct("name")
        elif location and storage_type:
            query = self.queryset.filter(
                location__address__icontains=location,
                storage_unit__storage_unit_type__in=storage_type.split(),
                storage_unit__is_available=True,
            ).distinct("name")
        elif location and size == 1:
            if small_size == 1 and medium_size == 1 and large_size == 1:
                query = self.queryset.filter(
                    free_space__range=(small, large),
                    location__address__icontains=location,
                    storage_unit__is_available=True,
                ).distinct("name")
            elif small_size == 1 and medium_size == 1:
                query = self.queryset.filter(
                    free_space__range=(small, medium),
                    location__address__icontains=location,
                    storage_unit__is_available=True,
                ).distinct("name")
            elif small_size == 1 and large_size == 1:
                query = self.queryset.filter(
                    free_space__range=(small, large),
                    location__address__icontains=location,
                    storage_unit__is_available=True,
                ).distinct("name")
            elif medium_size == 1 and large_size == 1:
                query = self.queryset.filter(
                    free_space__range=(medium, large),
                    location__address__icontains=location,
                    storage_unit__is_available=True,
                ).distinct("name")
            elif large_size == 1:
                query = self.queryset.filter(
                    free_space__range=(5000, large),
                    location__address__icontains=location,
                    storage_unit__is_available=True,
                ).distinct("name")
            elif medium_size == 1:
                query = self.queryset.filter(
                    free_space=(2500, medium),
                    location__address__icontains=location,
                    storage_unit__is_available=True,
                ).distinct("name")
            elif small_size == 1:
                query = self.queryset.filter(
                    free_space__range=(small, 1000),
                    location__address__icontains=location,
                    storage_unit__is_available=True,
                ).distinct("name")
        elif location:
            query = self.queryset.filter(
                location__address__icontains=location, storage_unit__is_available=True
            ).distinct("name")
        else:
            return Response(
                {"msg": "no storage found at this location"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if query:
            page = self.paginate_queryset(query)

            if page is not None:
                serializer = self.get_serializer(page, many=True)

                return self.get_paginated_response(serializer.data)

            serializer = self.serializer_class(query, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"msg": "no storage found at this location"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class StorageUnitViewEndUser(generics.ListAPIView):
    """
    This for end user to get all rooms of a specific storage provider
    """

    serializer_class = StorageUnitSerializer
    permission_classes = [AllowAny]
    queryset = StorageUnit.objects.all()

    def get_queryset(self, *args, **kwargs):
        facility_id = self.kwargs["facility_id"]
        storage_unit = self.queryset.filter(storage_facility__id=facility_id)
        return storage_unit


class DetailStorageUnitViewEndUser(generics.ListAPIView):
    """
    This for end user to get specific storage unit of storage facilitator
    """

    serializer_class = StorageUnitSerializer
    permission_classes = [AllowAny]
    queryset = StorageUnit.objects.all()

    def get_queryset(self, *args, **kwargs):
        facility_id = self.kwargs["facility_id"]
        storage_id = self.kwargs["storage_id"]
        storage_unit = self.queryset.filter(
            storage_facility__id=facility_id, id=storage_id
        )
        return storage_unit


class DetailStorageFacilityView(generics.GenericAPIView, RetrieveModelMixin):
    """
    Filter StorageUnit and list them
    """

    serializer_class = StorageFacilitesSerialzier
    permission_classes = [AllowAny]
    queryset = StorageFacility.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CreateFeatureView(generics.CreateAPIView):
    """
    This View is used to add a new feature in storage facility
    """

    serializer_class = CreateFeatureSerializer
    permission_classes = [IsServiceProvider]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeleteFeatureView(
    generics.GenericAPIView, UpdateModelMixin, DestroyModelMixin
):
    """
    This is used to update retrieve and delete Feature
    """

    serializer_class = FeatureSerialzier
    permission_classes = [IsServiceProvider]
    queryset = Feature.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CreateImageView(generics.CreateAPIView):
    """
    This View is used to add a new feature in storage facility
    """

    serializer_class = CreateImageSerializer
    permission_classes = [IsServiceProvider]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteImageView(generics.GenericAPIView, DestroyModelMixin):
    """
    This is used to update retrieve and delete Feature
    """

    serializer_class = ImageSerializer
    permission_classes = [IsServiceProvider]
    queryset = Images.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

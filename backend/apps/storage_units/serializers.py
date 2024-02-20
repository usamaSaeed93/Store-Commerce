from django.contrib.gis.geos import Point
from django.db.models import Min
from rest_framework import serializers

from apps.service_providers.serializers import (
    LocationSerializer,
    StorageUnitProviderSerializer,
    UserSerializer,
)

from .models import *


class GetRatingsSerializer(serializers.ModelSerializer):
    """This serializer is used for Get ratings serializers
    and in it there is no nested storage facility serializer
    so better response"""

    user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Ratings
        fields = ["id", "user", "facility_ratings", "comment"]


class StorageUnitsSerializer(serializers.ModelSerializer):
    """This is also a nested serializer used to give detail view
    of storage facility in admin panel of storage facility"""

    size_field = serializers.SerializerMethodField()
    free_space_field = serializers.SerializerMethodField()
    occupied_space_field = serializers.SerializerMethodField()

    class Meta:
        model = StorageUnit
        fields = [
            "id",
            "name",
            "size",
            "storage_unit_type",
            "per_unit_price",
            "free_space",
            "occupied_space",
            "size_field",
            "free_space_field",
            "occupied_space_field",
            "description",
            "is_available",
            "is_occupied",
            "created_at",
        ]

    def get_size_field(self, obj):
        return obj.size_field

    def get_free_space_field(self, obj):
        return obj.free_space_field

    def get_occupied_space_field(self, obj):
        return obj.occupied_space_field


class ImageSerializer(serializers.ModelSerializer):
    """
    This serialzier is used in Storage Facility as nested serializer
    """

    class Meta:
        model = Images
        fields = "__all__"


class FeatureSerialzier(serializers.ModelSerializer):
    """
    Nested serializer to create features of a storage Facility
    """

    class Meta:
        model = Feature
        fields = ["id", "features_text"]


class StorageFacilitySerializer(serializers.ModelSerializer):
    """
    in this serializer location will be get and created and
    storage facility will be updated and created
    """

    storage_provider = StorageUnitProviderSerializer(many=False, read_only=True)
    storage_provider_ids = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, queryset=StorageUnitProvider.objects.all()
    )
    location = LocationSerializer(many=False, read_only=False)
    total_size_field = serializers.SerializerMethodField()
    free_space_field = serializers.SerializerMethodField()
    occupied_space_field = serializers.SerializerMethodField()
    storage_unit = StorageUnitsSerializer(many=True, read_only=True)
    facility_images = ImageSerializer(many=True, required=False)
    features = FeatureSerialzier(many=True, required=False)
    facility_ratings = GetRatingsSerializer(read_only=True, many=True)

    class Meta:
        model = StorageFacility
        fields = [
            "id",
            "name",
            "storage_provider",
            "location",
            "storage_provider_ids",
            "working_hours",
            "total_size",
            "free_space",
            "total_storage_units",
            "occupied_space",
            "total_size_field",
            "free_space_field",
            "occupied_space_field",
            "available_storage_units",
            "occupied_storage_unit",
            "address",
            "description",
            "storage_unit",
            "access_hours",
            "is_online",
            "minimum_price",
            "facility_images",
            "features",
            "facility_ratings",
            "created_at",
        ]

    def get_total_size_field(self, obj):
        return obj.total_size_field

    def get_free_space_field(self, obj):
        return obj.free_space_field

    def get_occupied_space_field(self, obj):
        return obj.occupied_space_field

    def create(self, validated_data):
        location = validated_data.pop("location", None)
        storage_provider = validated_data.pop("storage_provider_ids", None)
        facility_images = validated_data.pop("facility_images", None)
        features = validated_data.pop("features", None)

        try:
            location = Location.objects.get(lat=location["lat"], lon=location["lon"])
        except:
            location = Location.objects.create(
                address=location["address"],
                city=location["city"],
                country=location["country"],
                country_code=location["country_code"],
                county=location["county"],
                postcode=location["postcode"],
                district=location["district"],
                lat=location["lat"],
                lon=location["lon"],
                point=Point(location["lon"], location["lat"]),
            )
        storage_facility = StorageFacility.objects.create(
            location=location, storage_provider=storage_provider, **validated_data
        )
        if facility_images:
            for image in facility_images:
                Images.objects.create(storage_facility=storage_facility, **image)
        if features:
            for data in features:
                Feature.objects.create(storage_facility=storage_facility, **data)

        return storage_facility

    def update(self, instance, validated_data):
        location = validated_data.pop("location", None)
        try:
            location = Location.objects.get(lat=location["lat"], lon=location["lon"])
        except:
            location = Location.objects.create(
                address=location["address"],
                city=location["city"],
                country=location["country"],
                country_code=location["country_code"],
                county=location["county"],
                postcode=location["postcode"],
                district=location["district"],
                lat=location["lat"],
                lon=location["lon"],
                point=Point(location["lon"], location["lat"]),
            )
        instance.name = validated_data.get("name", instance.name)
        instance.address = validated_data.get("address", instance.address)
        instance.description = validated_data.get("description", instance.description)
        instance.is_online = validated_data.get("is_online", instance.is_online)
        instance.working_hours = validated_data.get(
            "working_hours", instance.working_hours
        )
        instance.access_hours = validated_data.get(
            "access_hours", instance.access_hours
        )
        instance.location = location
        instance.save()

        return instance


class RatingsSerializer(serializers.ModelSerializer):

    """
    This serialzier is used to create and caluclate average ratings
    """

    storage_facility = StorageFacilitySerializer(many=False, read_only=True)
    user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Ratings
        fields = ["user", "storage_facility", "facility_ratings", "comment"]

    def create(self, validated_data):
        validated_data["user"] = self.context["user"]
        validated_data["storage_facility"] = self.context["storage_facility"]
        reviews = Ratings.objects.create(**validated_data)
        print(reviews)
        if reviews:
            facility = StorageFacility.objects.get(
                id=validated_data["storage_facility"].id
            )
            if facility.total_persons_rating is None:
                facility.total_persons_rating = 0
            if facility.average_rating is None:
                facility.average_rating = 0
            if facility.total_ratings is None:
                facility.total_ratings = 0
            facility.total_persons_rating += 1
            facility.total_ratings = (
                facility.total_ratings + validated_data["facility_ratings"]
            )
            facility.average_rating = (
                facility.total_ratings / facility.total_persons_rating
            )
            facility.save()
        return reviews


class StorageFacilitesSerialzier(serializers.ModelSerializer):
    """
    This serializer is used in Storage Unit Serializer for better response
    """

    storage_provider = StorageUnitProviderSerializer(many=False, read_only=True)
    total_size_field = serializers.SerializerMethodField()
    free_space_field = serializers.SerializerMethodField()
    occupied_space_field = serializers.SerializerMethodField()
    facility_ratings = GetRatingsSerializer(read_only=True, many=True)
    location = LocationSerializer(many=False, read_only=False)
    facility_images = ImageSerializer(read_only=True, many=True)
    storage_unit = StorageUnitsSerializer(read_only=True, many=True)
    features = FeatureSerialzier(many=True)

    class Meta:
        model = StorageFacility
        fields = [
            "id",
            "name",
            "storage_provider",
            "location",
            "total_size",
            "free_space",
            "total_storage_units",
            "occupied_space",
            "total_size_field",
            "free_space_field",
            "occupied_space_field",
            "available_storage_units",
            "occupied_storage_unit",
            "address",
            "description",
            "working_hours",
            "access_hours",
            "average_rating",
            "total_persons_rating",
            "is_online",
            "created_at",
            "facility_ratings",
            "facility_images",
            "features",
            "storage_unit",
        ]

    def get_total_size_field(self, obj):
        return obj.total_size_field

    def get_free_space_field(self, obj):
        return obj.free_space_field

    def get_occupied_space_field(self, obj):
        return obj.occupied_space_field


class StorageUnitSerializer(serializers.ModelSerializer):
    """
    This serialzier is used to create storage unit
    """

    storage_facility = StorageFacilitesSerialzier(many=False, read_only=True)
    storage_facility_ids = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, queryset=StorageFacility.objects.all()
    )
    size_field = serializers.SerializerMethodField()
    free_space_field = serializers.SerializerMethodField()
    occupied_space_field = serializers.SerializerMethodField()

    class Meta:
        model = StorageUnit
        fields = [
            "id",
            "name",
            "storage_facility",
            "size",
            "description",
            "per_unit_price",
            "free_space",
            "occupied_space",
            "storage_facility_ids",
            "size_field",
            "free_space_field",
            "occupied_space_field",
            "is_available",
            "is_occupied",
            "storage_unit_type",
            "created_at",
        ]

    def get_size_field(self, obj):
        return obj.size_field

    def get_free_space_field(self, obj):
        return obj.free_space_field

    def get_occupied_space_field(self, obj):
        return obj.occupied_space_field

    def create(self, validated_data):
        storage_facility_ids = validated_data.pop("storage_facility_ids", None)
        service_type_data = StorageUnit.objects.create(
            storage_facility=storage_facility_ids,
            name=validated_data["name"],
            size=validated_data["size"],
            free_space=validated_data["size"],
            occupied_space=0,
            is_available=validated_data["is_available"],
            is_occupied=False,
            per_unit_price=validated_data["per_unit_price"],
            description=validated_data["description"],
            storage_unit_type=validated_data["storage_unit_type"],
        )
        total_storage_unit = StorageUnit.objects.filter(
            storage_facility__id=storage_facility_ids.id
        )
        free_size = 0
        total_size = 0
        occupied_size = 0
        available_storage_units = 0
        occupied_storage_units = 0
        minimum = total_storage_unit.aggregate(Min("per_unit_price"))[
            "per_unit_price__min"
        ]

        for data in total_storage_unit:
            total_size += data.size
            free_size += data.free_space
            occupied_size += data.occupied_space
            if data.is_available:
                available_storage_units += 1
            if data.is_occupied:
                occupied_storage_units += 1

        storage_facility = StorageFacility.objects.get(id=storage_facility_ids.id)
        storage_facility.total_size = total_size
        storage_facility.free_space = free_size

        if storage_facility.total_storage_units is None:
            storage_facility.total_storage_units = 0
        if storage_facility.available_storage_units is None:
            storage_facility.available_storage_units = 0
        if storage_facility.occupied_storage_unit is None:
            storage_facility.occupied_storage_unit = 0
        if storage_facility.occupied_space is None:
            storage_facility.occupied_space = 0
        if storage_facility.minimum_price is None:
            storage_facility.minimum_price = 0

        storage_facility.available_storage_units = available_storage_units
        storage_facility.occupied_storage_unit = occupied_storage_units
        storage_facility.total_storage_units += 1
        storage_facility.minimum_price = minimum
        storage_facility.save()

        return service_type_data

    def update(self, instance, validated_data):
        check = validated_data.get("is_occupied", instance.is_occupied)
        if check:
            raise serializers.ValidationError(
                {"msg": "Storage unit is already booked you can update it right now."}
            )
        else:
            storage_facility_ids = validated_data.pop("storage_facility_ids")

            instance.size = validated_data.get("size", instance.size)
            instance.name = validated_data.get("name", instance.name)
            instance.description = validated_data.get(
                "description", instance.description
            )
            instance.free_space = instance.size - instance.occupied_space
            instance.occupied_space = instance.size - instance.free_space
            instance.is_available = validated_data.get(
                "is_available", instance.is_available
            )
            instance.per_unit_price = validated_data.get(
                "per_unit_price", instance.per_unit_price
            )
            instance.storage_unit_type = validated_data.get(
                "storage_unit_type", instance.storage_unit_type
            )
            instance.save()
            total_units = StorageUnit.objects.filter(
                storage_facility__id=storage_facility_ids.id
            )
            free_size = 0
            total_size = 0
            available_storage_units = 0
            occupied_storage_units = 0
            minimum = total_units.aggregate(Min("per_unit_price"))[
                "per_unit_price__min"
            ]

            for data in total_units:
                total_size += data.size
                free_size += data.free_space
                if data.is_available:
                    available_storage_units += 1
                if data.is_occupied:
                    occupied_storage_units += 1
                    if data.is_available:
                        data.is_available = False
                        if data.is_available == 0:
                            data.is_available = 0
                        else:
                            available_storage_units -= 1
                data.save()

        storage_facility = StorageFacility.objects.get(id=storage_facility_ids.id)
        storage_facility.total_size = total_size
        storage_facility.free_space = free_size

        if storage_facility.occupied_space is None:
            storage_facility.occupied_space = 0
        if storage_facility.available_storage_units is None:
            storage_facility.available_storage_units = 0
        if storage_facility.occupied_storage_unit is None:
            storage_facility.occupied_storage_unit = 0
        if storage_facility.minimum_price is None:
            storage_facility.minimum_price = 0

        storage_facility.occupied_space = total_size - free_size
        storage_facility.available_storage_units = available_storage_units
        storage_facility.occupied_storage_unit = occupied_storage_units
        storage_facility.minimum_price = minimum
        storage_facility.save()

        return instance


class StorageUnitsTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageUnit
        fields = ["storage_unit_type"]


class SearchStorageFacilitesSerialzier(serializers.ModelSerializer):
    """
    This serializer is used just for Searching Storage Facilities
    """

    storage_provider = StorageUnitProviderSerializer(many=False, read_only=True)
    location = LocationSerializer(many=False, read_only=False)
    facility_images = ImageSerializer(read_only=True, many=True)
    storage_unit = StorageUnitsTypesSerializer(read_only=True, many=True)

    class Meta:
        model = StorageFacility
        fields = [
            "id",
            "name",
            "storage_provider",
            "location",
            "address",
            "description",
            "working_hours",
            "access_hours",
            "is_online",
            "created_at",
            "average_rating",
            "total_persons_rating",
            "facility_images",
            "minimum_price",
            "storage_unit",
        ]


class CreateFeatureSerializer(serializers.ModelSerializer):
    """
    This Serialzier is created to post a new feature in facility object
    """

    storage_facility_id = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, queryset=StorageFacility.objects.all()
    )

    class Meta:
        model = Feature
        fields = ["id", "storage_facility_id", "features_text"]

    def create(self, validated_data):
        facility_id = validated_data.pop("storage_facility_id", None)
        feature = Feature.objects.create(
            storage_facility=facility_id, features_text=validated_data["features_text"]
        )
        return feature


class CreateImageSerializer(serializers.ModelSerializer):
    """
    This Serialzier is created to post a new image in facility object
    """

    storage_facility_id = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, queryset=StorageFacility.objects.all()
    )

    class Meta:
        model = Images
        fields = ["storage_facility_id", "image"]

    def create(self, validated_data):
        facility_id = validated_data.pop("storage_facility_id", None)
        feature = Images.objects.create(
            storage_facility=facility_id, image=validated_data["image"]
        )
        return feature


class GetStorageUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageUnit
        fields = ["name"]


class GetStorageFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageFacility
        fields = ["name"]

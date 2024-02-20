import os

from celery import Celery
from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from apps.service_providers.models import Location
from apps.service_providers.serializers import LocationSerializer, UserSerializer
from apps.storage_units.models import StorageFacility, StorageUnit
from apps.storage_units.serializers import (
    StorageFacilitesSerialzier,
    StorageUnitProviderSerializer,
)

from .models import *

# constant envoirments which will be used further
celery = Celery()
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")


class LocationSerializer(serializers.ModelSerializer):
    """
    Location serializer is used for nested
    relations of serializer
    """

    class Meta:
        model = Location
        fields = ["address"]


class GetStorageFacilitesSerialzier(serializers.ModelSerializer):
    """
    This serializer is used in Storage Unit Serializer to get ids
    of storage unit.
    """

    class Meta:
        model = StorageFacility
        fields = ["id"]


class StorageUnitSerializer(serializers.ModelSerializer):
    """
    Created for nested intitalizationd of serialziers.
    """

    storage_facility = GetStorageFacilitesSerialzier(many=False, read_only=True)
    size_field = serializers.SerializerMethodField()

    class Meta:
        model = StorageUnit
        fields = [
            "id",
            "storage_facility",
            "size_field",
            "name",
            "description",
            "per_unit_price",
        ]

    def get_size_field(self, obj):
        return obj.size_field


class StorageFacilitesSerialzier(serializers.ModelSerializer):
    """
    This serializer is used in Storage Unit Serializer for better response
    """

    storage_provider = StorageUnitProviderSerializer(many=False, read_only=True)
    location = LocationSerializer(many=False, read_only=False)
    total_size_field = serializers.SerializerMethodField()

    class Meta:
        model = StorageFacility
        fields = [
            "id",
            "name",
            "storage_provider",
            "total_size_field",
            "location",
            "address",
            "working_hours",
            "access_hours",
        ]

    def get_total_size_field(self, obj):
        return obj.total_size_field


class StorageUnitDetailSerializer(serializers.ModelSerializer):
    """
    Provide details accordingly so that can be used in
    nested serializers.
    """

    storage_facility = StorageFacilitesSerialzier(many=False, read_only=True)
    size_field = serializers.SerializerMethodField()

    class Meta:
        model = StorageUnit
        fields = [
            "id",
            "size_field",
            "storage_unit_type",
            "name",
            "per_unit_price",
            "storage_facility",
        ]

    def get_size_field(self, obj):
        return obj.size_field


class CartSerialzier(serializers.ModelSerializer):
    """
    This serializer is used to create cart of a user
    to add products in it and get that cart.
    """

    user = UserSerializer(read_only=True, many=False)
    storage_unit = StorageUnitSerializer(many=True, read_only=True)
    storage_unit_ids = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, queryset=StorageUnit.objects.all()
    )

    class Meta:
        model = Cart
        fields = ["id", "user", "storage_unit", "storage_unit_ids", "created_at"]

    def create(self, validated_data):
        storage_unit = validated_data.pop("storage_unit_ids", None)
        validated_data["user"] = self.context["user"]
        try:
            cart = Cart.objects.get(user=validated_data["user"])
        except:
            cart = Cart.objects.create(**validated_data)
        if storage_unit:
            cart.storage_unit.add(storage_unit)

        return cart


class StorageFacilityOrderSerialzier(serializers.ModelSerializer):
    """
    This serialzier facilitated UserOrderSerialzier for nested creation
    """

    storage_unit_ids = serializers.PrimaryKeyRelatedField(
        many=False, write_only=True, queryset=StorageUnit.objects.all()
    )

    class Meta:
        model = StorageFacilityOrder
        fields = [
            "id",
            "storage_unit_ids",
            "pending",
            "completed",
            "starting_date",
            "ending_date",
            "months",
        ]


class UserOrderSerilaizer(serializers.ModelSerializer):
    """
    This seriliazer is just to create order for end user
    to post orders.
    """

    user = UserSerializer(read_only=True, many=False)
    order = StorageFacilityOrderSerialzier(many=True)

    class Meta:
        model = UserOrder
        fields = ["id", "user", "business_type", "total_price", "order"]

    def create(self, validated_data):
        """
        Override default method of serialzier create, as
        we are creating writable nested seriable.
        """

        validated_data["user"] = self.context["user"]
        order_data = validated_data.pop("order", None)
        order_place = UserOrder.objects.create(
            user=validated_data["user"], business_type=validated_data["business_type"]
        )
        total_price = 0
        if order_data:
            for data in order_data:
                starting_date = data["starting_date"]
                month = data["months"]
                ending_date = starting_date + relativedelta(months=+month)
                unit_id = data.pop("storage_unit_ids", None)
                unit = StorageUnit.objects.get(id=unit_id.id)
                if unit.is_occupied:
                    order_place.delete()
                    raise serializers.ValidationError(
                        {"msg": f"Storage {unit.name} is already booked"}
                    )
                if unit.free_space == 0:
                    order_place.delete()
                    raise serializers.ValidationError(
                        {"msg": f"Storage {unit.name} is already booked"}
                    )
                unit.is_occupied = True
                unit.is_available = False
                unit.free_space -= unit.size
                unit.occupied_space += unit.size
                total_price += month * unit.per_unit_price
                unit.save()
                facility = StorageFacility.objects.get(id=unit.storage_facility.id)
                facility.free_space -= unit.size
                facility.occupied_space += unit.size
                facility.available_storage_units -= 1
                facility.occupied_storage_unit += 1
                facility.save()
                storage_order = StorageFacilityOrder.objects.create(
                    order=order_place,
                    months=month,
                    unit_order=unit,
                    starting_date=starting_date,
                    ending_date=ending_date,
                )
                celery.send_task(  # Celery to configuration to send mail
                    "send_admin_order_email",  # for forget password
                    kwargs={
                        "email": storage_order.unit_order.storage_facility.storage_provider.email,
                        "user_email": storage_order.order.user.email,
                        "order_id": storage_order.order.slug,
                        "facility_name": storage_order.unit_order.storage_facility.name,
                        "facility_city": storage_order.unit_order.storage_facility.location.city,
                        "facility_country": storage_order.unit_order.storage_facility.location.country,
                        "facility_address": storage_order.unit_order.storage_facility.address,
                        "facility_working_hours": storage_order.unit_order.storage_facility.working_hours,
                        "facility_access_hours": storage_order.unit_order.storage_facility.access_hours,
                        "storage_name": storage_order.unit_order.name,
                        "move_in_reason": storage_order.order.business_type,
                        "move_in_date": storage_order.starting_date,
                        "end_in_date": storage_order.ending_date,
                        "storage_price": (
                            month * storage_order.unit_order.per_unit_price
                        ),
                    },
                )
            order_place.total_price = total_price
            order_place.save()
            units = []
            for data in order_place.order.all():
                val = {
                    "name": data.unit_order.name,
                    "price": data.unit_order.per_unit_price,
                    "starting_date": data.starting_date,
                    "ending_date": data.ending_date,
                }
                units.append(val)

            celery.send_task(  # Celery to configuration to send mail
                "send_order_email",  # for forget password
                kwargs={
                    "email": order_place.user.email,
                    "order_id": order_place.slug,
                    "business_type": order_place.business_type,
                    "total_price": order_place.total_price,
                    "storage_unit": units,
                },
            )
            cart = Cart.objects.get(user=order_place.user)
            cart.delete()
        else:
            order_place.delete()
            raise serializers.ValidationError({"msg": "your cart is empty"})
        return order_place


class UserOrderAdminSerializer(serializers.ModelSerializer):
    """
    This serializer is used for admin orders retrievel of data
    """

    user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = UserOrder
        fields = ["slug", "user", "business_type"]


class StorageFacilityOrderAdminSerialzier(serializers.ModelSerializer):
    """
    This serialzier is used to show orders of admin
    """

    order = UserOrderAdminSerializer(many=False, read_only=True)
    unit_order = StorageUnitSerializer(many=False, read_only=True)

    class Meta:
        model = StorageFacilityOrder
        fields = [
            "id",
            "order",
            "unit_order",
            "pending",
            "completed",
            "starting_date",
            "ending_date",
            "months",
        ]


class StorageFacilityOrderDetailSerialzier(serializers.ModelSerializer):
    """
    This serialzier is used to show the details of order and update order
    """

    order = UserOrderAdminSerializer(many=False, read_only=True)
    unit_order = StorageUnitDetailSerializer(many=False, read_only=True)

    class Meta:
        model = StorageFacilityOrder
        fields = [
            "id",
            "order",
            "unit_order",
            "pending",
            "completed",
            "starting_date",
            "ending_date",
            "months",
        ]

    def update(self, instance, validated_data):
        """
        This is method will over ride the existing
        serializer default update method.
        """
        instance.pending = validated_data.get("pending", instance.pending)
        instance.completed = validated_data.get("completed", instance.completed)
        instance.save()
        return instance


class GetUserOrderSerialzier(serializers.ModelSerializer):
    """
    This serialzier will get orders of user
    against who is autheticated.
    """

    user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = UserOrder
        fields = ["id", "user", "slug", "business_type", "total_price", "created_at"]


class StorageFacilityUserOrderDetailSerialzier(serializers.ModelSerializer):
    """
    This serialzier facilitates GetUserOrderDetailSerialzier for nested creation.
    """

    unit_order = StorageUnitSerializer(many=False, read_only=True)

    class Meta:
        model = StorageFacilityOrder
        fields = [
            "id",
            "unit_order",
            "pending",
            "completed",
            "feedback",
            "starting_date",
            "ending_date",
            "months",
        ]


class GetUserOrderDetailSerialzier(serializers.ModelSerializer):
    """
    This serialzier will get the complete detail of
    user order
    """

    user = UserSerializer(read_only=True, many=False)
    order = StorageFacilityUserOrderDetailSerialzier(many=True, read_only=True)

    class Meta:
        model = UserOrder
        fields = [
            "id",
            "user",
            "slug",
            "business_type",
            "total_price",
            "created_at",
            "order",
        ]


class MoverOrderSerialzier(serializers.ModelSerializer):
    """
    This Serializer is for Mover Order
    """

    user = UserSerializer(read_only=True, many=False)
    from_location = LocationSerializer(many=False, read_only=False)

    class Meta:
        model = MoverOrder
        fields = [
            "id",
            "user",
            "from_location",
            "business_type",
            "reasons",
            "pending",
            "proccess",
            "completed",
            "from_date",
            "to_date",
            "mover_order",
            "size",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """
        This method overrides the default method of
        serialzier create.
        """

        validated_data["user"] = self.context["request"].user
        location = validated_data.pop("from_location", None)
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
            )
        mover_order = MoverOrder.objects.create(
            from_location=location, **validated_data
        )
        return mover_order

    def update(self, instance, validated_data):
        """
        This will override the default method of update
        in serialziers.
        """

        instance.pending = validated_data.get("pending", instance.pending)
        instance.proccess = validated_data.get("proccess", instance.proccess)
        instance.completed = validated_data.get("completed", instance.completed)
        instance.save()
        return instance


class OrganizerOrderSerialzier(serializers.ModelSerializer):
    """
    This Serializer is for Organizer Order
    """

    user = UserSerializer(read_only=True, many=False)
    from_location = LocationSerializer(many=False, read_only=False)
    to_location = LocationSerializer(many=False, read_only=False)

    class Meta:
        model = OraganizerOrder
        fields = [
            "id",
            "user",
            "from_location",
            "business_type",
            "reasons",
            "pending",
            "proccess",
            "completed",
            "from_date",
            "to_date",
            "organizer_order",
            "to_location",
            "size",
            "time",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """
        This method overrides the default method of
        serialzier create.
        """

        validated_data["user"] = self.context["request"].user
        location = validated_data.pop("from_location", None)
        to_location = validated_data.pop("to_location", None)
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
            )
        try:
            to_location = Location.objects.get(
                lat=to_location["lat"], lon=to_location["lon"]
            )
        except:
            to_location = Location.objects.create(
                address=to_location["address"],
                city=to_location["city"],
                country=to_location["country"],
                country_code=to_location["country_code"],
                county=to_location["county"],
                postcode=to_location["postcode"],
                district=to_location["district"],
                lat=to_location["lat"],
                lon=to_location["lon"],
            )
        organizer_order = OraganizerOrder.objects.create(
            from_location=location, to_location=to_location, **validated_data
        )
        return organizer_order

    def update(self, instance, validated_data):
        """
        This will override the default method of update
        in serialziers.
        """
        instance.pending = validated_data.get("pending", instance.pending)
        instance.proccess = validated_data.get("proccess", instance.proccess)
        instance.completed = validated_data.get("completed", instance.completed)
        instance.save()

        return instance

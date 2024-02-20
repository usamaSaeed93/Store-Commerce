from rest_framework import serializers

from apps.Auth.models import User

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "address",
            "city",
            "country",
            "country_code",
            "county",
            "postcode",
            "district",
            "lat",
            "lon",
        ]


class MoverSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)
    location = LocationSerializer(many=True, read_only=True)
    location_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Location.objects.all()
    )

    class Meta:
        model = Movers
        fields = [
            "id",
            "name",
            "user",
            "phone_number",
            "fax_number",
            "email",
            "website",
            "facebook",
            "instagram",
            "twitter",
            "google_buisness",
            "working_hours",
            "location",
            "location_ids",
        ]

    def create(self, validated_data):
        locations = validated_data.pop("location_ids", None)
        try:
            mover = Movers.objects.get(name=validated_data["name"])
        except:
            validated_data["user"] = self.context["request"].user
            mover = Movers.objects.create(**validated_data)
        if locations:
            mover.location.set(locations)

        return mover

    def update(self, instance, validated_data):
        location_data = validated_data.pop("location_ids")
        location = (instance.location).all()
        location = list(location)
        instance.name = validated_data.get("name", instance.name)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.fax_number = validated_data.get("fax_number", instance.fax_number)
        instance.email = validated_data.get("email", instance.email)
        instance.website = validated_data.get("website", instance.website)
        instance.facebook = validated_data.get("facebook", instance.facebook)
        instance.instagram = validated_data.get("instagram", instance.instagram)
        instance.twitter = validated_data.get("twitter", instance.twitter)
        instance.google_buisness = validated_data.get(
            "google_buisness", instance.google_buisness
        )
        instance.working_hours = validated_data.get(
            "working_hours", instance.working_hours
        )
        instance.save()
        if location_data:
            instance.location.set(location_data)

        return instance


class OrganizerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)
    location = LocationSerializer(many=True, read_only=True)
    location_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Location.objects.all()
    )

    class Meta:
        model = Organizers
        fields = [
            "id",
            "name",
            "user",
            "phone_number",
            "fax_number",
            "email",
            "website",
            "facebook",
            "instagram",
            "twitter",
            "google_buisness",
            "unit_numbers",
            "size",
            "location",
            "location_ids",
        ]

    def create(self, validated_data):
        locations = validated_data.pop("location_ids", None)
        try:
            organizer = Organizers.objects.get(name=validated_data["name"])
        except:
            validated_data["user"] = self.context["request"].user
            organizer = Organizers.objects.create(**validated_data)
        if locations:
            organizer.location.set(locations)

        return organizer

    def update(self, instance, validated_data):
        location_data = validated_data.pop("location_ids")
        location = (instance.location).all()
        location = list(location)
        instance.name = validated_data.get("name", instance.name)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.fax_number = validated_data.get("fax_number", instance.fax_number)
        instance.email = validated_data.get("email", instance.email)
        instance.website = validated_data.get("website", instance.website)
        instance.facebook = validated_data.get("facebook", instance.facebook)
        instance.instagram = validated_data.get("instagram", instance.instagram)
        instance.twitter = validated_data.get("twitter", instance.twitter)
        instance.google_buisness = validated_data.get(
            "google_buisness", instance.google_buisness
        )
        instance.unit_numbers = validated_data.get(
            "unit_numbers", instance.unit_numbers
        )
        instance.size = validated_data.get("size", instance.size)
        instance.save()
        if location_data:
            instance.location.set(location_data)

        return instance


class StorageUnitProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = StorageUnitProvider
        fields = [
            "id",
            "name",
            "user",
            "phone_number",
            "fax_number",
            "email",
            "website",
            "facebook",
            "instagram",
            "twitter",
            "google_buisness",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        try:
            storage_unit_provider = StorageUnitProvider.objects.get(
                user=validated_data["user"]
            )
        except:
            storage_unit_provider = StorageUnitProvider.objects.create(**validated_data)
            if storage_unit_provider:
                user_validation = User.objects.get(id=storage_unit_provider.user.id)
                user_validation.is_provider_verified = True
                user_validation.save()

        return storage_unit_provider

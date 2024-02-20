import os

from celery import Celery
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from apps.Auth.models import User

# constant envoirments which will be used further.
celery = Celery()
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer will get all the user feilds.
    """

    class Meta:
        model = User
        fields = "__all__"


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    This serialzier is used to for changing password.
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("old_password", "password", "password2")

    def validate(self, attrs):
        """
        This method will validate the passwords.
        """

        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def validate_old_password(self, value):
        """
        This will validate if the old password is
        correct.
        """

        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return value

    def update(self, instance, validated_data):
        """
        This method will basically update the
        password.
        """

        user = self.context["request"].user
        if user.pk != instance.pk:
            raise serializers.ValidationError(
                {"authorize": "You don't have permission to update this user."}
            )
        instance.set_password(validated_data["password"])
        instance.save()

        return instance


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    This method will update user details or profile.
    """

    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email",)

    def validate_email(self, value):
        """
        This method will validate new user mail if it exists
        it will raise a error else update.
        """

        user = self.context["request"].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                {"email": "This email is already in use."}
            )
        return value

    def update(self, instance, validated_data):
        """
        This method will update the user and send mail
        to verify its new user.
        """

        user = self.context["request"].user
        if user.email == validated_data["email"]:
            raise serializers.ValidationError(
                {"authorize": "Enter a different email address to update"}
            )
        if user.pk != instance.pk:
            raise serializers.ValidationError(
                {"authorize": "You don't have permission to update this user."}
            )
        instance.email = validated_data["email"]
        id = urlsafe_base64_encode(force_bytes(user.pk))

        celery.send_task(  # Celery to configuration to send mail
            "send_verification_email",  # for user account verification
            kwargs={
                "email": validated_data["email"],
                "id": id,
            },
        )
        instance.save()
        return instance

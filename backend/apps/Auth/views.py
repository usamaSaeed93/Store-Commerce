import os

import django.contrib.auth.password_validation as validators
from asgiref.sync import async_to_sync
from celery import Celery
from channels.layers import get_channel_layer
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.Auth.jwttoken import get_tokens_for_user
from apps.Auth.messages import *
from apps.Auth.models import User
from apps.Auth.serializers import (
    ChangePasswordSerializer,
    UpdateUserSerializer,
    UserSerializer,
)
from utils.generatetoken import ActivationTokenGenerator

# constant envoirments which will be used further
FRONTEND_URL = os.getenv("FRONT_URL")
home_url = os.getenv("SERVER_URL")
celery = Celery()
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")


# Create your views here.
class Login(APIView):
    """
    In this view user will be authenticated and
    give access to site.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        In this post method user will add its credentials
        like email and password to get access of site.
        """

        email = request.data.get("email", None)
        password = request.data.get("password", None)
        if email is None or password is None:
            return Response(
                {"msg": EMAIL_PASSWORD_REQUIRED},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = User.objects.get(email=email)
        except:
            return Response(
                {"msg": USER_NOT_VALID},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            if not user.is_verified:
                return Response(
                    {"msg": USER_NOT_VERIFIED},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user.check_password(password):
                token = get_tokens_for_user(user)
                return Response(
                    {
                        "msg": SUCCESS_LOGIN,
                        "refresh": token["refresh"],
                        "access": token["access"],
                        "user_id": urlsafe_base64_encode(force_bytes(user.pk)),
                        "service_provider": user.is_service_provider,
                        "is_provider_verified": user.is_provider_verified,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"msg": USER_NOT_VALID},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class Register(APIView):
    """
    In this view user will be registered.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        In this post method user will add its credentials
        to register itself as a service provide or end user
        after this a verification mail will be sent to user.
        """

        email = request.data.get("email", None)
        password = request.data.get("password", None)
        is_service_provider = request.data.get("is_service_provider")
        if len(password) > 8:
            validators.validate_password(password)
            if email is None or password is None:
                return Response(
                    {"msg": EMAIL_PASSWORD_REQUIRED},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                user = User.objects.get(email=email)
            except:
                user = User.objects.create(
                    email=email, is_service_provider=is_service_provider
                )
                user.set_password(password)
                user.save()
                id = urlsafe_base64_encode(force_bytes(user.pk))

                celery.send_task(  # Celery to configuration to send mail
                    "send_verification_email",  # for user account verification
                    kwargs={"email": user.email, "id": id, "home_url": home_url},
                )

                return Response(
                    {"msg": SUCCESS_REGISTER},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"msg": USER_ALREADY_EXISTS},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"msg": "password length should be greater than 8 characters"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyUser(APIView):
    """
    This is a handler used to verify user
    from email response.
    """

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        """
        This method will have a get request which will
        extract id from url parameters and verify user
        true if available.
        """

        is_verified = False
        message = "User not valid"
        user_id = request.query_params.get("id", None)
        if user_id is None:
            return Response(
                {
                    "message": message,
                    "verified": is_verified,
                },
                template_name="auth/verify_user.html",
            )

        # get the user and verify
        try:
            id = force_str(urlsafe_base64_decode(user_id))
            user = User.objects.get(id=id)
        except:
            return Response(
                {
                    "message": message,
                    "verified": is_verified,
                },
                template_name="auth/verify_user.html",
            )
        message = "User Verified"
        is_verified = True
        user.is_verified = is_verified
        user.save()
        return Response(
            {
                "message": message,
                "verified": is_verified,
                "url": f"{FRONTEND_URL}/sign-in",
                "button_txt": "Back to Sign In",
            },
            template_name="auth/verify_user.html",
        )


class ViewAll(APIView):
    """
    This is view can view all
    users and admin user has
    access to it only.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        This is the get request which will
        get all users based on permissions
        """

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)


class Logout(APIView):
    """
    This view is used for authenticated user
    which will call it and logout.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        This is the post method when api hit on this method
        user will logout by taking refresh token.
        """

        try:
            refresh_token = request.data["refresh_token"]
            user_id = request.data["user_id"]
            user_id = force_str(urlsafe_base64_decode(user_id))
            token = RefreshToken(refresh_token)
            token.blacklist()
            """channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "disconnect",
            }
        )"""
            return Response(
                {"msg": LOGGED_OUT},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ViewUser(APIView):
    """
    This is view is used by authenticated user
    to look at its profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        This method will get user_id
        and show its profile accordingly
        """

        current_user = request.user
        if current_user.id != user_id:
            return Response(
                {"msg": "User not Verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserSerializer(current_user)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)


class ResetPassword(APIView):
    """
    This view is used to if user forgets password
    it can call it to reset their password.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        This is the method in which user enter its
        credentials and new password and email is sent
        to him/her to change to new password.
        """

        email = request.data.get("email", None)
        new_password = request.data.get("new_password", None)
        if email is None or new_password is None:
            return Response(
                {
                    "msg": EMAIL_PASSWORD_REQUIRED,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        users = list(User.objects.filter(email=email))
        if users:
            user = users[0]
            token = ActivationTokenGenerator()
            token_key = token.make_token(user)
            id = urlsafe_base64_encode(force_bytes(user.pk))
            encoded_password = urlsafe_base64_encode(force_bytes(new_password))
            celery.send_task(  # Celery to configuration to send mail
                "send_email",  # for forget password
                kwargs={
                    "reset_code": token_key,
                    "email": user.email,
                    "id": id,
                    "passowrd": encoded_password,
                    "home_url": home_url,
                },
            )
            return Response(
                {
                    "msg": "Email Send Successfully",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "msg": USER_NOT_EXIST,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResetPasswordHandler(APIView):
    """
    This view allows user to verify user by clicking
    on link provided in email to update its password.
    """

    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        """
        This method verifies the user and updates its password.
        """
        reset_code = request.query_params.get("code", None)
        user_id = request.query_params.get("id", None)
        encoded_password = request.query_params.get("pass", None)
        message = "Code Not Valid"
        is_verified = False
        if reset_code is None or user_id is None or encoded_password is None:
            return Response(
                {
                    "message": message,
                    "verified": is_verified,
                },
                template_name="auth/verify_user.html",
            )

        # get the password and reset it
        try:
            id = force_str(urlsafe_base64_decode(user_id))
            new_password = force_str(urlsafe_base64_decode(encoded_password))
            user = User.objects.get(id=id)
        except:
            return Response(
                {
                    "message": message,
                    "verified": is_verified,
                },
                template_name="auth/verify_user.html",
            )
        token = ActivationTokenGenerator()
        if token.check_token(user, reset_code):
            user.set_password(new_password)
            user.save()
            message = "Password Changed Successfully"
            is_verified = True
            return Response(
                {
                    "message": message,
                    "verified": is_verified,
                    "url": f"{FRONTEND_URL}/sign-in",
                    "button_txt": "Back to Sign In",
                },
                template_name="auth/verify_user.html",
            )
        return Response(
            {
                "message": message,
                "verified": is_verified,
            },
            template_name="auth/verify_user.html",
        )


class ChangePassword(generics.UpdateAPIView):
    """
    This view basically allow user to change password
    when logged in.
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        """
        This user method will allow user to update password
        by authenticating it.
        """

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "msg": "Password Updated Successfully",
            },
            status=status.HTTP_200_OK,
        )


class UpdateUser(generics.UpdateAPIView):
    """
    This method will update the User profile if
    it is authenticated.
    """

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer

    def update(self, request, *args, **kwargs):
        """
        This method will update the user and send verification
        mail to verify user again.
        """

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "msg": "An email sent for verification of this email",
            },
            status=status.HTTP_200_OK,
        )

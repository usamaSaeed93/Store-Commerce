import os

from celery import Celery
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, views, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.service_providers.permissions import IsServiceProvider

from .models import *
from .serializers import *

celery = Celery()
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
# Create your views here.


class CartView(views.APIView):
    """This is the cart of user its get post and put method"""

    permission_classes = [IsAuthenticated]
    serializer_class = CartSerialzier

    def get(self, request):
        cart = Cart.objects.filter(user=self.request.user)
        if cart.exists():
            serializer = self.serializer_class(cart, many=True)
            return Response(serializer.data)
        else:
            return Response(
                {"msg: your cart is empty"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"user": self.request.user}
        )
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = self.request.user
        cart = Cart.objects.get(user=user)
        storage_unit_ids = request.data.get("storage_unit_ids", None)
        if storage_unit_ids is None:
            return Response(
                {"msg": "storage unit cannot be none"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.storage_unit.remove(storage_unit_ids)
        cart.save()
        return Response(
            {"msg": "Successfully updated cart"}, status=status.HTTP_201_CREATED
        )


class OrderPlaceView(views.APIView):
    """This view is used to create order"""

    permission_classes = [IsAuthenticated]
    serializer_class = UserOrderSerilaizer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"user": self.request.user}
        )
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAdminStorageUnitOrderView(generics.ListAPIView):
    """Get the all orders of service providers"""

    permission_classes = [IsServiceProvider]
    serializer_class = StorageFacilityOrderAdminSerialzier
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["pending", "completed", "starting_date", "ending_date"]
    search_fields = ["order__slug", "unit_order__name"]

    def get_queryset(self):
        query_set = StorageFacilityOrder.objects.filter(
            unit_order__storage_facility__storage_provider__user=self.request.user
        )
        return query_set


class GetRecentAdminStorageFacilityView(views.APIView):
    """Get the recent 5 orders of service providers"""

    permission_classes = [IsServiceProvider]
    serializer_class = StorageFacilityOrderAdminSerialzier

    def get(self, request):
        order = StorageFacilityOrder.objects.filter(
            unit_order__storage_facility__storage_provider__user=self.request.user
        )[:5]
        if order:
            serializer = self.serializer_class(order, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"msg": "No orders till yet"}, status=status.HTTP_404_NOT_FOUND
            )


class UpdateStorageOrderAdmin(views.APIView):
    """This is to get detail view of order and update it"""

    permission_classes = [IsServiceProvider]
    serializer_class = StorageFacilityOrderDetailSerialzier

    def get(self, request, order_id):
        order = StorageFacilityOrder.objects.get(id=order_id)
        if order:
            serializer = self.serializer_class(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"msg": "No orders are placed till yet"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def patch(self, request, order_id):
        order = StorageFacilityOrder.objects.get(id=order_id)
        if order.completed:
            return Response(
                {"msg": "Order is already Completed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.serializer_class(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            if serializer.data["completed"]:
                storage_unit = StorageUnit.objects.get(id=order.unit_order.id)
                storage_unit.free_space = storage_unit.size
                storage_unit.occupied_space = (
                    storage_unit.free_space - storage_unit.size
                )
                storage_unit.is_occupied = False
                storage_unit.is_available = True
                storage_unit.save()
                storage_facility = StorageFacility.objects.get(
                    id=storage_unit.storage_facility.id
                )
                storage_facility.free_space += storage_unit.size
                storage_facility.occupied_space -= storage_unit.size
                storage_facility.available_storage_units += 1
                storage_facility.occupied_storage_unit -= 1
                storage_facility.save()
            if serializer.data["pending"] and serializer.data["completed"]:
                celery.send_task(  # Celery to configuration to send mail
                    "send_order_email_user",  # for user order updation
                    kwargs={
                        "pending": serializer.data["pending"],
                        "completed": serializer.data["completed"],
                        "storage_name": order.unit_order.name,
                        "email": order.order.user.email,
                        "provider_name": order.unit_order.storage_facility.storage_provider.name,
                        "order_id": order.order.slug,
                    },
                )
            elif serializer.data["pending"]:
                celery.send_task(  # Celery to configuration to send mail
                    "send_order_email_user",  # for user order updation
                    kwargs={
                        "pending": serializer.data["pending"],
                        "completed": serializer.data["completed"],
                        "email": order.order.user.email,
                        "storage_name": order.unit_order.name,
                        "provider_name": order.unit_order.storage_facility.storage_provider.name,
                        "order_id": order.order.slug,
                    },
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdateStorageOrderUser(views.APIView):
    """
    This is the view to update status of the order feedback
    when user post the feedback of order this api will be called
    to update the status of order
    """

    permission_classes = [IsAuthenticated]
    serializer_class = StorageFacilityOrderDetailSerialzier

    def patch(self, request, order_id):
        try:
            order = StorageFacilityOrder.objects.get(id=order_id)
            if order.completed:
                order.feedback = True
                order.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"msg": "Order not completed so feedback cannot be added"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GetUserStorageFacilityView(generics.ListAPIView):
    """This view is used to list all orders of an end user"""

    permission_classes = [IsAuthenticated]
    serializer_class = GetUserOrderSerialzier
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["slug"]
    filterset_fields = ["business_type"]

    def get_queryset(self):
        query_set = UserOrder.objects.filter(user=self.request.user)
        return query_set


class GetUserDetailStorageFacilityOrderView(views.APIView):
    """This is the detail view of order for an end  user"""

    permission_classes = [IsAuthenticated]
    serializer_class = GetUserOrderDetailSerialzier

    def get(self, request, order_id):
        order = UserOrder.objects.get(id=order_id)
        if order:
            serializer = self.serializer_class(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"msg": "No orders placed till yet"}, status=status.HTTP_404_NOT_FOUND
            )


class GetUserDetailStorageUnitView(views.APIView):
    """This is the detail view of order for an end  user"""

    permission_classes = [IsAuthenticated]
    serializer_class = GetUserOrderDetailSerialzier

    def get(self, request, order_id):
        order = UserOrder.objects.get(id=order_id)
        if order:
            serializer = self.serializer_class(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"msg": "No orders placed till yet"}, status=status.HTTP_404_NOT_FOUND
            )


class MoverOrderViewset(viewsets.ModelViewSet):
    """An end user can see to whom he has given order of mover"""

    permission_classes = [IsAuthenticated]
    queryset = MoverOrder.objects.all()
    serializer_class = MoverOrderSerialzier
    http_method_names = ["get", "post", "head", "delete"]

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class OrganizersOrderViewset(viewsets.ModelViewSet):
    """An end user can see to whom he has given order of organizers"""

    permission_classes = [IsAuthenticated]
    queryset = OraganizerOrder.objects.all()
    serializer_class = OrganizerOrderSerialzier
    http_method_names = ["get", "post", "head", "delete"]

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class AdminMoverOrderViewset(viewsets.ModelViewSet):
    """An admin user can see from whom he has got orders"""

    permission_classes = [IsServiceProvider]
    queryset = MoverOrder.objects.all()
    serializer_class = MoverOrderSerialzier
    http_method_names = ["get", "head", "patch", "delete"]

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(mover_order__user=self.request.user)
        return query_set


class AdminOrganizersOrderViewset(viewsets.ModelViewSet):
    """An admin user can see from whom he has got orders"""

    permission_classes = [IsServiceProvider]
    queryset = OraganizerOrder.objects.all()
    serializer_class = OrganizerOrderSerialzier
    http_method_names = ["get", "head", "patch", "delete"]

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(organizer_order__user=self.request.user)
        return query_set

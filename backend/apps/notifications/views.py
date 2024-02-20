from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serialziers import *


# Create your views here.
class NotificationViews(APIView):
    """
    This view is to show all users
    their specific notification
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        This method will basically post notification and store it
        in db
        """
        serializer = NotificationSerializer(
            data=request.data, context={"request": self.request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateNotificationViews(APIView):
    """
    This view is to show all users
    their specific notification
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        """
        This method will basically post notification and store it
        in db
        """
        notification = Notifications.objects.get(id=id)
        serializer = NotificationSerializer(
            notification, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

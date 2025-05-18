from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions

from .models import Role
from .serializers import RoleSerializer
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from edu_track.backends import CustomJWTAuthentication
from edu_track.decorators import adminRequired


@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
class RoleListCreateView(APIView):
    @adminRequired
    def get(self, request):
        roles = Role.objects.filter(isDeleted=False)
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    @adminRequired
    def post(self, request):
        serializer = RoleSerializer(
            data=request.data, context={"createdBy": request.user.id}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
class RoleDetailView(APIView):
    def get_object(self, pk):
        try:
            return Role.objects.get(pk=pk, isDeleted=False)
        except Role.DoesNotExist:
            raise exceptions.NotFound()

    @adminRequired
    def get(self, request, pk):
        role = self.get_object(pk)
        serializer = RoleSerializer(role)
        return Response(serializer.data)

    @adminRequired
    def put(self, request, pk):
        role = self.get_object(pk)
        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @adminRequired
    def delete(self, request, pk):
        role = self.get_object(pk)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Create your views here.

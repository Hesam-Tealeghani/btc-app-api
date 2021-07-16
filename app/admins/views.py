from rest_framework import authentication, generics, permissions, status, viewsets, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
import datetime

from django.contrib.auth import get_user_model
from django.http import Http404

from admins.serializers import AdminSerializer, AuthTokenSerializer, ProfileSerializer, ProfileImageSerializer, EditProfileSerializer, CreatingAdminSerializer, ChangePasswordSerializer
from core.models import User

class CreateAdminView(generics.CreateAPIView):
    """Create a new admin"""
    serializer_class = AdminSerializer    
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)


class CreateTokenView(ObtainAuthToken):
    """Create a token for loged in admin"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        serialize_user = CreatingAdminSerializer(user)
        token, created = Token.objects.get_or_create(user=user)
        admin = get_object_or_404(get_user_model(), pk=serialize_user.data['id'])
        admin.last_login = datetime.datetime.now()
        admin.save()
        return Response({
            'token': token.key,
            'user': serialize_user.data
        })


class ManageUserView(generics.RetrieveUpdateAPIView):
    """retrieving and editing profile for authenticated admins"""
    serializer_class = ProfileSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = get_user_model().objects.all()

    def get_object(self):
        """Retrieve and return the authenticated admin"""
        return self.request.user

    def get_serializer_class(self):
        """The apropriate serializer class for editing profile"""
        if self.request.method == "PATCH":
            return EditProfileSerializer
        return self.serializer_class


class ListUsersView(generics.ListAPIView):
    """The viewset to handle admins listing"""
    serializer_class = ProfileSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    queryset = get_user_model().objects.all()

    def filter_queryset(self,queryset):
        """To order by name"""
        return self.queryset.order_by('name')


class PromotingAdmin(APIView):
    """The view to manage promote or demote admins"""
    serializer_class = AdminSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    prermission_classes = (permissions.IsAdminUser,)

    def post(self, request, pk):
        admin = get_object_or_404(get_user_model(), pk=pk)
        admin.is_staff = not(admin.is_staff)
        admin.save()
        return Response(status=status.HTTP_200_OK)


class DeactiveAdmin(APIView):
    """The api view to active and deactivate admins"""
    serializer_class = AdminSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, pk):
        admin = get_object_or_404(get_user_model(), pk=pk)
        admin.is_active = not(admin.is_active)
        admin.save()
        return Response(status=status.HTTP_200_OK)


class AdminProfileAPIView(generics.RetrieveAPIView):
    """The API view to see other admins profile"""
    serializer_class = ProfileSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = get_user_model().objects.all()


class ChangePictureAPIView(generics.UpdateAPIView):
    serializer_class = ProfileImageSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = get_user_model().objects.all()

    def get_object(self):
        """Retrieve and return the authenticated admin"""
        return self.request.user


class ChangePassword(APIView):
    """The api view to change the password"""
    serializer_class = ChangePasswordSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def get_object(self):
        """Retrieve and return the authenticated admin"""
        return self.request.user

    def post(self, request):
        admin = get_object()
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        if admin.check_password(old_password):
            if new_password == request.data['confirm_password']:
                admin.set_password(new_password)
                admin.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': "Passwords does not match!"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': "Incorrect Password"})

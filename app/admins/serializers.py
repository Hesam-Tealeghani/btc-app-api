from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

class AdminSerializer(serializers.ModelSerializer):
    """Model Serializer for admin objects"""
    nation = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'name', 'address', 'phone', 'postal_code', 'birth_date', 'is_active',
                  'email', 'is_staff', 'password', 'title', 'nationality', 'nation'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 6
            }, 
            'id': {
                'read_only': True
            }
        }
    
    def create(self, validated_data):
        """To use the create_user function and creat an admin with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        """Edit the admin and set the password correctly and return it"""
        password = validated_data.pop('password', None)
        admin = super().update(instance, validated_data)

        if password:
            admin.set_password(password)
            admin.save()
        return admin
    
    def get_nation(self, obj):
        return str(obj.nationality)


class ProfileSerializer(serializers.ModelSerializer):
    """The serializer to see other admins"""
    nation = serializers.SerializerMethodField()
    last_log = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'name', 'address', 'phone', 'postal_code', 'birth_date', 'is_active',
                  'email', 'is_staff', 'title', 'nationality', 'nation', 'last_log'
        )

    def get_nation(self, obj):
        return str(obj.nationality)

    def get_last_log(self, obj):
        if obj.last_login:
            return str(obj.last_login.year) + '/' + str(obj.last_login.month) + '/' + str(obj.last_login.day) + '   ' + str(obj.last_login.hour) + ':' + str(obj.last_login.minute)
        else:
            return None

class AuthTokenSerializer(serializers.Serializer):
    """The Serializer class for the admin authentication object"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type':'password'}, 
        trim_whitespace=False
    )

    def validate(self, attrs):
        """To validate and authenticate the admin request attributes"""
        username = attrs.get('username')
        password = attrs.get('password')
        admin = authenticate(
            request=self.context.get('requset'),
            username=username,
            password=password
        )
        if not admin:
            msg = "Authentication Failed"
            raise serializers.ValidationError(msg, code='authentication')
        attrs['user'] = admin
        return attrs

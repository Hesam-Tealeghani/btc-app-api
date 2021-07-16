from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from core.models import Country


def dateToString(date):
    """Change the date format"""
    year = date.year
    month = date.month 
    day = date.day

    if month < 10:
        month = '0' + str(month)

    if day < 10:
        day = '0' + str(day)

    return str(year) + '-' + str(month) + '-' + str(day)


def dateTimeToString(datetime):
    """Change the date time format"""
    year = datetime.year
    month = datetime.month
    day = datetime.day
    hour = datetime.hour
    minute = datetime.minute

    if month < 10:
        month = '0' + str(month)

    if day < 10:
        month = '0' + str(day)

    return str(year) + '-' + str(month) + '-' + str(day) + '   ' + str(hour) + ':' + str(minute)

class NationalitySerializer(serializers.ModelSerializer):
    """The minima serializer for other models using nationality field"""
    class Meta:
        model = Country
        fields = ['id', 'name', 'abreviation']
        read_only_fields = ['id', 'name', 'abreviation']

class AdminSerializer(serializers.ModelSerializer):
    """Model Serializer for admin objects"""
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'name', 'address', 'phone', 'postal_code', 'birth_date', 'is_active',
                  'email', 'is_staff', 'password', 'title', 'nationality'
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
        return get_user_model().objects.create_user(**validated_data, image="uploads/user/e0ed03f5-7525-43af-936d-dae54d7d27c1.png")
    

class EditProfileSerializer(serializers.ModelSerializer):
    """The Serializer to edit Profiles"""
    class Meta:
        model = get_user_model()
        fields = ['id', 'name', 'address', 'phone', 'postal_code', 'birth_date', 'email', 'nationality']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    """The serializer to see other admins"""
    nationality = NationalitySerializer(read_only=True)
    last_log = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'name', 'address', 'phone', 'postal_code', 'birth_date', 'is_active',
                  'email', 'is_staff', 'title', 'nationality', 'last_log', 'image'
        )
        read_only_fields = ['id', 'username', 'is_active', 'is_staff', 'title', 'image']

    def get_last_log(self, obj):
        if obj.last_login:
            return dateTimeToString(obj.last_login)
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


class ProfileImageSerializer(serializers.ModelSerializer):
    """serializer for uploading images to profile"""
    class Meta:
        model = get_user_model()
        fields = ['image']


class CreatingAdminSerializer(serializers.ModelSerializer):
    """The Minimal Serializer to send informations of an admin in another Model"""
    class Meta:
        model = get_user_model()
        fields = ['id', 'image', 'name']
        read_only_fields = ['id', 'image', 'name']


class ChangePasswordSerializer(serializers.ModelSerializer):
    """The serializer class to change the password"""
    class Meta:
        model = get_user_model()
        fields = ['password']
        read_only_fields = ['id', 'image', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 6
            }
        }
    
    def update(self, instance, validated_data):
        """Edit the admin and set the password correctly and return it"""
        password = validated_data.pop('password', None)
        
        if password:
            if len(password) < 6:
                raise ValidationError('Too short')
            else:
                admin.set_password(password)
                admin.save()
        else:
            raise ValidationError('Password can not be empty')
        return admin

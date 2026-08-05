from rest_framework import serializers
from users.models import User

class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'last_name', 'is_staff')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = ('username', 'email', 'name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self,validated_data):
        return User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            name = validated_data.get('name'),
            last_name = validated_data.get('last_name'),
            password = validated_data['password'],
        )

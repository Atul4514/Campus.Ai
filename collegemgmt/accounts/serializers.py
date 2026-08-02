from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CollegeIDAllowlist

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'college_id', 'role', 'department', 'phone', 'is_verified']
        read_only_fields = ['id', 'is_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    college_id = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'college_id', 'password', 'department', 'phone']

    def validate_college_id(self, value):
        try:
            allowlist_entry = CollegeIDAllowlist.objects.get(college_id=value)
        except CollegeIDAllowlist.DoesNotExist:
            raise serializers.ValidationError("Invalid college ID. Not in allowlist.")
        if allowlist_entry.is_used:
            raise serializers.ValidationError("This college ID is already registered.")
        return value

    def create(self, validated_data):
        college_id = validated_data.pop('college_id')
        password = validated_data.pop('password')

        allowlist_entry = CollegeIDAllowlist.objects.get(college_id=college_id)
        allowlist_entry.is_used = True
        allowlist_entry.save()

        user = User.objects.create_user(
            college_id=college_id,
            password=password,
            role=allowlist_entry.role,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
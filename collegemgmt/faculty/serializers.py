from rest_framework import serializers
from .models import FacultyProfile, SubjectAssignment
from accounts.serializers import UserSerializer


class SubjectAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectAssignment
        fields = ['id', 'subject', 'section']


class FacultyProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    subject_assignments = SubjectAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = FacultyProfile
        fields = [
            'id', 'user', 'employee_id', 'designation', 'qualification',
            'experience_years', 'joined_date',
            'subject_assignments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FacultyProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyProfile
        fields = ['employee_id', 'designation', 'qualification', 'experience_years', 'joined_date']

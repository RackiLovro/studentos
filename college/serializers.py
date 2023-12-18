from rest_framework import serializers
from .models import Student, Course, Lecture, Administrator, EnrollmentRequest

class StudentSerializer(serializers.ModelSerializer):
    courses = serializers.PrimaryKeyRelatedField(many=True, queryset=Course.objects.all(), required=False)

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'birth_date', 'birth_place', 'completed_school', 'courses', 'average_grade', 'matriculation_grade']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'

class AdministratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = '__all__'

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'student', 'course', 'approved', 'approved_by', 'approval_reason', 'approval_date']

from rest_framework.decorators import action
from rest_framework import viewsets, status
from .models import Student, Course, Lecture, Administrator, EnrollmentRequest
from .serializers import StudentSerializer, CourseSerializer, LectureSerializer, AdministratorSerializer, EnrollmentRequestSerializer
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, url_path='course/(?P<course_id>\d+)', methods=['get'])
    def lectures_by_course(self, request, course_id=None):
        lectures = self.get_queryset().filter(course__id=course_id)
        serializer = self.get_serializer(lectures, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        username = request.data.get('email')
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Create the student profile
        student = Student(user=user, useusername=username, email=email, password=password)
        student.save()

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return Response({'token': token}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            student = Student.objects.get(user=user)
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            if student.first_login:
                return Response({'token': token, 'student_id': student.id, "status": "additional information required"}, status=status.HTTP_200_OK)
            else:
                return Response({'token': token, 'student_id': student.id}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete_profile(self, request, pk=None):
        student = self.get_object()
        data = request.data
        student.birth_date = data.get('birth_date')
        student.birth_place = data.get('birth_place')
        student.completed_school = data.get('completed_school')
        student.average_grade = data.get('average_grade')
        student.matriculation_grade = data.get('matriculation_grade')
        student.first_login = False
        student.save()
        return Response({"status": "profile completed"}, status=status.HTTP_200_OK)@action(detail=True, methods=['post'])
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        student = self.get_object()
        course_id = request.data.get('course_id')
        course = Course.objects.get(id=course_id)

        if EnrollmentRequest.objects.filter(student=student, course=course, approved=True).exists():
            return Response({"status": "You are already enrolled in this course"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            EnrollmentRequest.objects.create(student=student, course=course)
            return Response({"status": "Enrollment request created"}, status=status.HTTP_200_OK)
        
class AdministratorViewSet(viewsets.ModelViewSet):
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        username = request.data.get('email')
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Create the administrator profile
        administrator = Administrator(user=user, email = email)
        administrator.save()

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return Response({'token': token}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Response({'token': token}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'])
    def create_administrator(self, request):
        username = request.data.get('email')
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        administrator = Administrator(user=user, email = email)
        administrator.save()

        return Response({'status': 'Administrator created successfully'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete_administrator(self, request, pk=None):
        administrator = self.get_object()
        user = administrator.user
        user.delete()

        return Response({'status': 'Administrator deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def enroll_student(self, request):
        student_id = request.data.get('student_id')
        course_id = request.data.get('course_id')
        admin_id = request.data.get('admin_id')
        approval_reason = request.data.get('approval_reason')

        try:
            student = Student.objects.get(id=student_id)
            course = Course.objects.get(id=course_id)
            admin = Administrator.objects.get(id=admin_id)
            enrollment_request = EnrollmentRequest.objects.get(student=student, course=course, approved=False)  # Get the EnrollmentRequest instance
        except (Student.DoesNotExist, Course.DoesNotExist, Administrator.DoesNotExist, EnrollmentRequest.DoesNotExist):
            return Response({"status": "Student, Course, Administrator or Enrollment Request not found"}, status=status.HTTP_404_NOT_FOUND)

        if enrollment_request.approved:
            return Response({"status": "Student is already enrolled in this course"}, status=status.HTTP_400_BAD_REQUEST)

        enrollment_request.approved = True
        enrollment_request.approved_by = admin
        enrollment_request.approval_reason = approval_reason
        enrollment_request.approval_date = timezone.now()
        enrollment_request.save()

        return Response({"status": "Student enrolled in the course successfully"}, status=status.HTTP_200_OK)



    
class EnrollmentRequestViewSet(viewsets.ModelViewSet):
    queryset = EnrollmentRequest.objects.all()
    serializer_class = EnrollmentRequestSerializer

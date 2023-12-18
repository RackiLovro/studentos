from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, CourseViewSet, LectureViewSet, AdministratorViewSet, EnrollmentRequestViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lectures', LectureViewSet)
router.register(r'administrators', AdministratorViewSet)
router.register(r'enrollmentrequests', EnrollmentRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

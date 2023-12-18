from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=100)
    quota = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    ects = models.IntegerField(null=True, blank=True)

class Lecture(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    ects_points = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=100, null=True, blank=True)
    completed_school = models.CharField(max_length=100, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    lectures = models.ManyToManyField(Lecture, related_name='students')
    average_grade = models.FloatField(null=True, blank=True)
    matriculation_grade = models.FloatField(null=True, blank=True)
    first_login = models.BooleanField(default=True)

class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)

class EnrollmentRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Administrator, on_delete=models.SET_NULL, null=True, blank=True)
    approval_reason = models.TextField(null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

SESSION = [
        ('Tutorial', 'Tutorial'),
        ('Lecture', 'Lecture'),
        ('Lab', 'Lab'),
        ('Discussion', 'Discussion'),
        ('Presentation', 'Presentation'),
    ]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'ADMIN')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPES = (
        ('STUDENT', 'Student'),
        ('INSTRUCTOR', 'Instructor'),
        ('ADMIN', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=20, unique=True)
    programme = models.CharField(max_length=100)
    year_of_study = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.registration_number}"

class Department(models.Model):
    DepartmentName = models.CharField(max_length=100,primary_key=True)
    HeadOfDepartment = models.CharField(max_length=100)
    RegisteredDate = models.DateTimeField(auto_now_add=True)
    class Meta:
      verbose_name = "Department"
      verbose_name_plural = "Department"
    def __str__(self):
        return self.DepartmentName

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    office_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.user.get_full_name()

class TimeTableMain(models.Model):
    YearOfStudy = models.CharField(max_length=9)
    Programme = models.CharField(max_length=100)
    Semister = models.CharField(max_length=100)
    Department = models.ForeignKey(Department, on_delete=models.CASCADE)
    RegisteredDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.Programme} - {self.Semister} ({self.YearOfStudy})"

    class Meta:
        unique_together = ('Programme', 'YearOfStudy', 'Semister')
  
class CourseName(models.Model):
    Course = models.CharField(max_length=5)
    CourseCode = models.CharField(max_length=100,primary_key=True)
    RegisteredDate = models.DateTimeField(auto_now_add=True)
    CourseDescription= models.CharField(max_length=200)
    def __str__(self):
        return self.Course
    class Meta:
        unique_together = (('Course', 'CourseCode'),)

class Venue(models.Model):
    Venue = models.CharField(max_length=50,primary_key=True)
    RegisteredDate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.Venue
 

class TimeTable(models.Model):
    CourseName = models.ForeignKey(CourseName, on_delete=models.CASCADE)
    Instructor=models.ForeignKey(Instructor,on_delete=models.CASCADE)   
    Venue = models.ForeignKey(Venue,on_delete=models.CASCADE) 
    Timestart = models.TimeField()
    TimeEnd = models.TimeField()
    Day = models.CharField(max_length=100, choices=DAY_CHOICES)
    Programme=models.ForeignKey(TimeTableMain,on_delete=models.CASCADE)   
    RegisteredDate = models.DateTimeField(auto_now_add=True)
    SessionType= models.CharField(max_length=100, choices=SESSION)
     
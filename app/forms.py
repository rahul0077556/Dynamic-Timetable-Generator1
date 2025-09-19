from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student, Instructor, Department

class StudentSignUpForm(UserCreationForm):
    registration_number = forms.CharField(max_length=20)
    programme = forms.CharField(max_length=100)
    year_of_study = forms.CharField(max_length=20)
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'registration_number', 'programme', 'year_of_study')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'STUDENT'
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                registration_number=self.cleaned_data.get('registration_number'),
                programme=self.cleaned_data.get('programme'),
                year_of_study=self.cleaned_data.get('year_of_study')
            )
        return user

class InstructorSignUpForm(UserCreationForm):
    specialization = forms.CharField(max_length=100)
    office_number = forms.CharField(max_length=20, required=False)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department"
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'specialization', 'office_number', 'department')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'INSTRUCTOR'
        user.department = self.cleaned_data.get('department')
        if commit:
            user.save()
            Instructor.objects.create(
                user=user,
                specialization=self.cleaned_data.get('specialization'),
                office_number=self.cleaned_data.get('office_number')
            )
        return user

class EmailTimetableForm(forms.Form):
    email = forms.EmailField(label='Email Address')
    day = forms.ChoiceField(choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ])
    programme = forms.CharField(widget=forms.HiddenInput(), required=False) 
from django.shortcuts import render
from . models import *
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect
from .forms import EmailTimetableForm, StudentSignUpForm, InstructorSignUpForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.conf import settings
from .algorithms.genetic_algorithm import GeneticTimetableAlgorithm
from django.contrib.auth import login
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

        # Get the current date
today = datetime.now()
# Calculate the date of Monday and Friday of the current week
monday = today - timedelta(days=today.weekday())
friday = monday + timedelta(days=4)
# Get the current year
current_year = today.year
# Format the dates
monday_formatted = monday.strftime('%Y-%m-%d')
friday_formatted = friday.strftime('%Y-%m-%d')


def index(request):
    # Fetch distinct programmes, semesters, and years of study from TimeTableMain model
    programmes = TimeTableMain.objects.values_list('Programme', flat=True).distinct()
    semesters = TimeTableMain.objects.values_list('Semister', flat=True).distinct()
    years_of_study = TimeTableMain.objects.values_list('YearOfStudy', flat=True).distinct()

    # Fetch selected Programme and its Department when a POST request is made
    if request.method == 'POST':
        try:
            programme = request.POST.get('programme')
            semester = request.POST.get('semester')
            year_of_study = request.POST.get('year_of_study')

            # Use genetic algorithm to generate timetable
            ga = GeneticTimetableAlgorithm(
                population_size=50,
                mutation_rate=0.1,
                elite_size=2,
                generations=100
            )
            
            try:
                best_solution = ga.evolve(programme, semester, year_of_study)
                
                # Get the specific TimeTableMain instance
                timetable_main = TimeTableMain.objects.get(
                    Programme=programme,
                    Semister=semester,
                    YearOfStudy=year_of_study
                )
                
                # Convert solution to timetable entries
                timetable_entries = []
                for gene in best_solution.genes:
                    entry = TimeTable(
                        CourseName=gene.course,
                        Instructor=gene.instructor,
                        Venue=gene.venue,
                        Timestart=gene.time_start,
                        TimeEnd=gene.time_end,
                        Day=gene.day,
                        Programme=timetable_main,
                        SessionType=gene.session_type
                    )
                    timetable_entries.append(entry)

                # Group entries by day
                days = set(entry.Day for entry in timetable_entries)
                timetable_data = {day: [] for day in days}
                for entry in timetable_entries:
                    timetable_data[entry.Day].append(entry)

                context = {
                    'programmes': programmes,
                    'semesters': semesters,
                    'years_of_study': years_of_study,
                    'timetable_data': timetable_data,
                    'selected_programme': programme,
                    'department': timetable_main.Department,
                    'monday': monday_formatted,
                    'friday': friday_formatted,
                    'current_year': current_year,
                }
                return render(request, 'pages/index.html', context)
                
            except Exception as e:
                messages.error(request, f"Error generating timetable: {str(e)}")
                
        except Exception as e:
            messages.error(request, f"Error processing request: {str(e)}")

    # Default context for GET request or if POST fails
    context = {
        'programmes': programmes,
        'semesters': semesters,
        'years_of_study': years_of_study,
        'selected_programme': None,
        'department': None,
        'monday': monday_formatted,
        'friday': friday_formatted,
        'current_year': current_year,
    }

    return render(request, 'pages/index.html', context)
     

    
def support(request):
    return render(request, 'pages/support.html')

def signup(request):
    return redirect('landing')

@login_required
def dashboard(request):
    if request.user.user_type == 'STUDENT':
        return redirect('student_dashboard')
    elif request.user.user_type == 'INSTRUCTOR':
        return redirect('instructor_dashboard')
    elif request.user.user_type == 'ADMIN':
        return redirect('admin:index')
    return redirect('landing')

def send_timetable_email(request):
    if request.method == 'POST':
        form = EmailTimetableForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            day = form.cleaned_data['day']
            programme = form.cleaned_data['programme']

            # Get timetable entries for the selected day and programme
            timetable_entries = TimeTable.objects.filter(
                Day=day,
                Programme__Programme=programme
            ).order_by('Timestart')

            # Prepare email content
            context = {
                'day': day,
                'programme': programme,
                'timetable_entries': timetable_entries,
            }
            
            html_message = render_to_string('emails/timetable_email.html', context)
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject=f'Timetable for {day}',
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, 'Timetable has been sent to your email!')
            except Exception as e:
                messages.error(request, f'Failed to send email: {str(e)}')
            
            return redirect('dashboard')
    else:
        form = EmailTimetableForm()
    
    return render(request, 'pages/send_timetable.html', {'form': form})

def is_student(user):
    return user.is_authenticated and user.user_type == 'STUDENT'

def is_instructor(user):
    return user.is_authenticated and user.user_type == 'INSTRUCTOR'

def is_admin(user):
    return user.is_authenticated and user.user_type == 'ADMIN'

class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'registration/student_signup.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('student_dashboard')

class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'registration/instructor_signup.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('instructor_dashboard')

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    return render(request, 'pages/student_dashboard.html')

@login_required
@user_passes_test(is_instructor)
def instructor_dashboard(request):
    return render(request, 'pages/instructor_dashboard.html')

def landing_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'STUDENT':
            return redirect('student_dashboard')
        elif request.user.user_type == 'INSTRUCTOR':
            return redirect('instructor_dashboard')
        elif request.user.user_type == 'ADMIN':
            return redirect('admin:index')
    return render(request, 'pages/landing.html')

class StudentLoginView(LoginView):
    template_name = 'registration/student_login.html'
    
    def get_success_url(self):
        return reverse_lazy('student_dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        if user.user_type != 'STUDENT':
            form.add_error(None, "This login is only for students")
            return self.form_invalid(form)
        return super().form_valid(form)

class InstructorLoginView(LoginView):
    template_name = 'registration/instructor_login.html'
    
    def get_success_url(self):
        return reverse_lazy('instructor_dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        if user.user_type != 'INSTRUCTOR':
            form.add_error(None, "This login is only for instructors")
            return self.form_invalid(form)
        return super().form_valid(form)
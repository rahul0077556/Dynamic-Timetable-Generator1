from django.core.management.base import BaseCommand
from app.models import Department, Instructor, TimeTableMain, CourseName, Venue
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Populates the database with sample BTech data'

    def handle(self, *args, **kwargs):
        # First, delete existing data
        self.stdout.write('Cleaning existing data...')
        Department.objects.all().delete()
        Instructor.objects.all().delete()
        TimeTableMain.objects.all().delete()
        CourseName.objects.all().delete()
        Venue.objects.all().delete()

        # Create Departments
        departments_data = [
            {"DepartmentName": "Computer Science Engineering", "HeadOfDepartment": "Dr. Rajesh Kumar"},
            {"DepartmentName": "Electronics Engineering", "HeadOfDepartment": "Dr. Meena Gupta"},
            {"DepartmentName": "Mechanical Engineering", "HeadOfDepartment": "Dr. Suresh Verma"},
            {"DepartmentName": "Civil Engineering", "HeadOfDepartment": "Dr. Amit Patel"},
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept = Department.objects.create(**dept_data)
            departments[dept_data["DepartmentName"]] = dept

        # Create Instructors
        instructors_data = [
            # CSE Department
            {
                'username': 'dr.sharma',
                'password': make_password('password123'),
                'FirstName': 'Anil',
                'LastName': 'Sharma',
                'email': 'sharma@example.com',
                'Department': departments["Computer Science Engineering"],
                'is_staff': True
            },
            {
                'username': 'dr.patel',
                'password': make_password('password123'),
                'FirstName': 'Priya',
                'LastName': 'Patel',
                'email': 'patel@example.com',
                'Department': departments["Computer Science Engineering"],
                'is_staff': True
            },
            {
                'username': 'dr.gupta',
                'password': make_password('password123'),
                'FirstName': 'Rahul',
                'LastName': 'Gupta',
                'email': 'gupta@example.com',
                'Department': departments["Electronics Engineering"],
                'is_staff': True
            },
            {
                'username': 'dr.verma',
                'password': make_password('password123'),
                'FirstName': 'Suresh',
                'LastName': 'Verma',
                'email': 'verma@example.com',
                'Department': departments["Mechanical Engineering"],
                'is_staff': True
            },
        ]

        for instructor_data in instructors_data:
            Instructor.objects.create(**instructor_data)

        # Create Programs for each department and semester
        years = ['2023-24']
        semesters = ['Semester 1', 'Semester 2']
        
        for dept_name, dept in departments.items():
            program_name = f"BTech {dept_name.split()[0]}"  # e.g., "BTech Computer"
            for year in years:
                for semester in semesters:
                    TimeTableMain.objects.create(
                        Programme=program_name,
                        YearOfStudy=year,
                        Semister=semester,
                        Department=dept
                    )

        # Create Courses
        courses_data = [
            # CSE Courses
            {'Course': 'DSA', 'CourseCode': 'CS201', 'CourseDescription': 'Data Structures and Algorithms'},
            {'Course': 'COA', 'CourseCode': 'CS202', 'CourseDescription': 'Computer Organization and Architecture'},
            {'Course': 'DBMS', 'CourseCode': 'CS203', 'CourseDescription': 'Database Management Systems'},
            {'Course': 'OS', 'CourseCode': 'CS204', 'CourseDescription': 'Operating Systems'},
            {'Course': 'CN', 'CourseCode': 'CS205', 'CourseDescription': 'Computer Networks'},
            {'Course': 'AI', 'CourseCode': 'CS206', 'CourseDescription': 'Artificial Intelligence'},
            {'Course': 'ML', 'CourseCode': 'CS207', 'CourseDescription': 'Machine Learning'},
            {'Course': 'WEB', 'CourseCode': 'CS208', 'CourseDescription': 'Web Technologies'},
            {'Course': 'SE', 'CourseCode': 'CS209', 'CourseDescription': 'Software Engineering'},
            {'Course': 'TOC', 'CourseCode': 'CS210', 'CourseDescription': 'Theory of Computation'},
            # ECE Courses
            {'Course': 'DC', 'CourseCode': 'EC201', 'CourseDescription': 'Digital Circuits'},
            {'Course': 'AC', 'CourseCode': 'EC202', 'CourseDescription': 'Analog Circuits'},
            {'Course': 'EMF', 'CourseCode': 'EC203', 'CourseDescription': 'Electromagnetic Fields'},
            # Mechanical Courses
            {'Course': 'TOM', 'CourseCode': 'ME201', 'CourseDescription': 'Theory of Machines'},
            {'Course': 'FM', 'CourseCode': 'ME202', 'CourseDescription': 'Fluid Mechanics'},
            {'Course': 'HT', 'CourseCode': 'ME203', 'CourseDescription': 'Heat Transfer'},
        ]

        for course_data in courses_data:
            CourseName.objects.create(**course_data)

        # Create Venues
        venues_data = [
            {'Venue': 'Lab 101'}, {'Venue': 'Lab 102'}, {'Venue': 'Lab 103'},
            {'Venue': 'Classroom 201'}, {'Venue': 'Classroom 202'}, {'Venue': 'Classroom 203'},
            {'Venue': 'Seminar Hall 301'}, {'Venue': 'Seminar Hall 302'},
            {'Venue': 'Workshop 401'}, {'Venue': 'Workshop 402'},
        ]

        for venue_data in venues_data:
            Venue.objects.create(**venue_data)

        self.stdout.write(self.style.SUCCESS('Successfully populated database with BTech data')) 
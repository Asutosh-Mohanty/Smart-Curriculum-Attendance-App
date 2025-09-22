from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Student
from teachers.models import Teacher, Subject, Timetable
from admins.models import Degree, Branch, Group, GroupSubjectAssignment
from core.models import Announcement


class Command(BaseCommand):
    help = 'Set up demo data for the SIH project'

    def handle(self, *args, **options):
        self.stdout.write('Setting up demo data...')

        # Create demo users
        self.create_demo_users()
        self.create_demo_degrees_branches_groups()
        self.create_demo_subjects()
        self.create_demo_assignments()
        self.create_demo_timetable()
        self.create_demo_announcements()

        self.stdout.write(
            self.style.SUCCESS('Demo data setup completed successfully!')
        )

    def create_demo_users(self):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@sih.edu',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write('Created admin user')

        # Create demo teacher
        if not User.objects.filter(username='teacher1').exists():
            teacher_user = User.objects.create_user(
                username='teacher1',
                email='teacher1@sih.edu',
                password='password123',
                first_name='John',
                last_name='Smith'
            )
            Teacher.objects.create(
                user=teacher_user,
                employee_id='T001',
                department='Computer Science'
            )
            self.stdout.write('Created demo teacher')

        # Create demo students
        students_data = [
            ('student1', 'student1@sih.edu', 'Alice', 'Johnson', 'S001', 'Mathematics, Programming'),
            ('student2', 'student2@sih.edu', 'Bob', 'Wilson', 'S002', 'Science, Technology'),
            ('student3', 'student3@sih.edu', 'Carol', 'Brown', 'S003', 'Physics, Engineering'),
        ]

        for username, email, first_name, last_name, roll_number, interests in students_data:
            if not User.objects.filter(username=username).exists():
                student_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name
                )
                Student.objects.create(
                    user=student_user,
                    roll_number=roll_number,
                    interests=interests,
                    attendance_percentage=85.0
                )
                self.stdout.write(f'Created demo student: {first_name} {last_name}')

    def create_demo_subjects(self):
        teacher = Teacher.objects.first()
        if teacher:
            subjects_data = [
                ('Mathematics', 'MATH101'),
                ('Physics', 'PHYS101'),
                ('Computer Science', 'CS101'),
                ('Chemistry', 'CHEM101'),
                ('English', 'ENG101'),
            ]

            for name, code in subjects_data:
                if not Subject.objects.filter(code=code).exists():
                    Subject.objects.create(
                        name=name,
                        code=code,
                        teacher=teacher
                    )
                    self.stdout.write(f'Created subject: {name}')

    def create_demo_degrees_branches_groups(self):
        # Degrees
        btech, _ = Degree.objects.get_or_create(name='B.Tech')
        bsc, _ = Degree.objects.get_or_create(name='B.Sc')
        # Branches
        cse, _ = Branch.objects.get_or_create(name='Computer Science', defaults={'degree': btech})
        if not cse.degree_id:
            cse.degree = btech
            cse.save()
        ece, _ = Branch.objects.get_or_create(name='Electronics', defaults={'degree': btech})
        if not ece.degree_id:
            ece.degree = btech
            ece.save()
        math, _ = Branch.objects.get_or_create(name='Mathematics', defaults={'degree': bsc})
        if not math.degree_id:
            math.degree = bsc
            math.save()
        # Groups
        Group.objects.get_or_create(name='Group 1', branch=cse, degree=btech)
        Group.objects.get_or_create(name='Group 2', branch=cse, degree=btech)
        Group.objects.get_or_create(name='Group A', branch=math, degree=bsc)

    def create_demo_assignments(self):
        teacher = Teacher.objects.first()
        if not teacher:
            return
        # Map first few subjects to available groups
        groups = list(Group.objects.all()[:3])
        subjects = list(Subject.objects.filter(teacher=teacher)[:3])
        for g, s in zip(groups, subjects):
            GroupSubjectAssignment.objects.get_or_create(group=g, subject=s, teacher=teacher)

    def create_demo_timetable(self):
        subjects = Subject.objects.all()
        if subjects.exists():
            timetable_data = [
                ('Monday', '09:00', subjects[0], 'A101'),
                ('Monday', '10:00', subjects[1], 'B201'),
                ('Monday', '11:00', subjects[2], 'C301'),
                ('Tuesday', '09:00', subjects[0], 'A101'),
                ('Tuesday', '10:00', subjects[3], 'D401'),
                ('Wednesday', '09:00', subjects[1], 'B201'),
                ('Wednesday', '10:00', subjects[2], 'C301'),
            ]

            for day, time_slot, subject, room in timetable_data:
                if not Timetable.objects.filter(day=day, time_slot=time_slot).exists():
                    Timetable.objects.create(
                        day=day,
                        time_slot=time_slot,
                        subject=subject,
                        room_number=room
                    )

    def create_demo_announcements(self):
        admin_user = User.objects.filter(is_staff=True).first()
        if admin_user:
            announcements_data = [
                ('Welcome to SIH Smart Education System', 'Welcome to our new smart education platform. This system will help streamline attendance, material sharing, and communication between students and teachers.'),
                ('Mid-term Examination Schedule', 'Mid-term examinations will be conducted from March 15-20, 2024. Please check your individual schedules and prepare accordingly.'),
                ('Holiday Notice', 'The college will remain closed on March 8, 2024, on account of Holi. Classes will resume on March 9, 2024.'),
            ]

            for title, content in announcements_data:
                if not Announcement.objects.filter(title=title).exists():
                    Announcement.objects.create(
                        title=title,
                        content=content,
                        created_by=admin_user
                    )
                    self.stdout.write(f'Created announcement: {title}')



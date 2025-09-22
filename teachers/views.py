from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import models
import json
from datetime import timedelta

from core.models import Attendance, Material, Announcement
from core.utils import generate_qr_code, calculate_attendance_percentage
from .models import Subject, QRCode
from admins.models import GroupSubjectAssignment


@login_required
def teacher_dashboard(request):
    teacher = request.user.teacher
    
    # Get teacher's group-subject assignments
    assignments = GroupSubjectAssignment.objects.select_related('group', 'subject').filter(teacher=teacher)
    
    # Get recent materials uploaded by teacher
    materials = Material.objects.filter(uploaded_by=teacher).order_by('-upload_date')[:5]
    
    # No heavy attendance computation on dashboard; use dedicated view after selection
    attendance_reports = None
    
    # Get announcements (all + teachers only)
    announcements = Announcement.objects.filter(
        is_active=True
    ).filter(
        models.Q(target_audience='all') | models.Q(target_audience='teachers')
    ).order_by('-created_at')[:3]
    
    context = {
        'teacher': teacher,
        'assignments': assignments,
        'materials': materials,
        'attendance_reports': attendance_reports,
        'announcements': announcements,
    }
    return render(request, 'teachers/teacher_dashboard.html', context)


@login_required
def group_selection(request):
    """Step 1: Teacher selects a group/class"""
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    teacher = request.user.teacher
    assignments = GroupSubjectAssignment.objects.select_related('group', 'subject').filter(teacher=teacher)
    
    context = {
        'teacher': teacher,
        'assignments': assignments,
    }
    return render(request, 'teachers/group_selection.html', context)


@login_required
def group_dashboard(request, subject_id):
    """Step 2: Show QR attendance, upload materials, view reports for selected group"""
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    subject = get_object_or_404(Subject, id=subject_id, teacher=request.user.teacher)
    teacher = request.user.teacher
    
    # Students should be those in the selected assignment's group if exists
    from students.models import Student
    assignment = GroupSubjectAssignment.objects.filter(subject_id=subject_id, teacher=request.user.teacher).select_related('group').first()
    if assignment:
        students = Student.objects.filter(group=assignment.group)
    else:
        students = Student.objects.all()
    
    # Get attendance reports for this subject
    attendance_reports = []
    for student in students:
        percentage = calculate_attendance_percentage(student, subject)
        attendance_reports.append({
            'student': student,
            'percentage': percentage
        })
    
    # Get materials for this subject
    materials = Material.objects.filter(subject=subject, uploaded_by=teacher).order_by('-upload_date')
    
    context = {
        'subject': subject,
        'teacher': teacher,
        'students': students,
        'attendance_reports': attendance_reports,
        'materials': materials,
    }
    return render(request, 'teachers/group_dashboard.html', context)


@login_required
def generate_qr(request, subject_id):
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    subject = get_object_or_404(Subject, id=subject_id, teacher=request.user.teacher)
    
    if request.method == 'POST':
        # Create QR code data
        qr_data = {
            'subject_id': subject.id,
            'teacher_id': request.user.teacher.id,
            'timestamp': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(minutes=15)).isoformat()
        }
        
        # Generate QR code
        qr_string = json.dumps(qr_data)
        qr_image = generate_qr_code(qr_string)
        
        # Save QR code to database
        qr_code = QRCode.objects.create(
            subject=subject,
            teacher=request.user.teacher,
            expires_at=timezone.now() + timedelta(minutes=15),
            qr_data=qr_string
        )
        
        context = {
            'qr_image': qr_image,
            'subject': subject,
            'expires_at': qr_code.expires_at,
            'qr_string': qr_string,
        }
        return render(request, 'teachers/qr_display.html', context)
    
    # GET request - show form
    return render(request, 'teachers/generate_qr.html', {'subject': subject})


@login_required
def upload_material(request, subject_id):
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    
    subject = get_object_or_404(Subject, id=subject_id, teacher=request.user.teacher)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        description = request.POST.get('description', '')
        
        material = Material.objects.create(
            title=title,
            file=file,
            subject=subject,
            uploaded_by=request.user.teacher,
            description=description
        )
        
        messages.success(request, 'Material uploaded successfully!')
        return redirect('teachers:group_dashboard', subject_id=subject.id)
    
    return render(request, 'teachers/upload_material.html', {'subject': subject})


@login_required
def attendance_report(request, assignment_id):
    if not hasattr(request.user, 'teacher'):
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    assignment = get_object_or_404(
        GroupSubjectAssignment.objects.select_related('group', 'subject'),
        id=assignment_id,
        teacher=request.user.teacher
    )
    from students.models import Student
    students = Student.objects.filter(group=assignment.group)
    reports = []
    for s in students:
        percentage = calculate_attendance_percentage(s, assignment.subject)
        reports.append({'student': s, 'percentage': percentage})
    context = {
        'assignment': assignment,
        'reports': reports,
    }
    return render(request, 'teachers/attendance_report.html', context)
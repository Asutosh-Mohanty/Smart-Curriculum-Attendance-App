from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
import json

from core.models import Attendance, Material, Announcement
from core.utils import get_student_recommendation, calculate_attendance_percentage
from teachers.models import Subject


@login_required
def student_dashboard(request):
    student = request.user.student
    
    # Get attendance data
    attendance_data = []
    subjects = Subject.objects.all()
    for subject in subjects:
        percentage = calculate_attendance_percentage(student, subject)
        attendance_data.append({
            'subject': subject.name,
            'percentage': percentage
        })
    
    # Get AI recommendation
    ai_recommendation = get_student_recommendation(student)
    
    # Get materials
    materials = Material.objects.all().order_by('-upload_date')[:5]
    
    # Get announcements (all + students only)
    announcements = Announcement.objects.filter(
        is_active=True
    ).filter(
        models.Q(target_audience='all') | models.Q(target_audience='students')
    ).order_by('-created_at')[:3]
    
    context = {
        'student': student,
        'attendance_data': attendance_data,
        'ai_recommendation': ai_recommendation,
        'materials': materials,
        'announcements': announcements,
    }
    return render(request, 'students/student_dashboard.html', context)


@login_required
def scan_qr(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Access denied.')
        return redirect('students:dashboard')
    
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data')
        try:
            data = json.loads(qr_data)
            subject = get_object_or_404(Subject, id=data['subject_id'])
            
            # Check if QR code is still valid
            from teachers.models import QRCode
            qr_code = QRCode.objects.filter(
                subject=subject,
                teacher_id=data['teacher_id'],
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()
            
            if not qr_code:
                return JsonResponse({'success': False, 'message': 'QR code expired or invalid.'})
            
            # Mark attendance
            attendance, created = Attendance.objects.get_or_create(
                student=request.user.student,
                subject=subject,
                date=timezone.now().date(),
                defaults={'is_present': True}
            )
            
            if not created:
                attendance.is_present = True
                attendance.save()
            
            # Update student's overall attendance percentage
            request.user.student.attendance_percentage = calculate_attendance_percentage(request.user.student)
            request.user.student.save()
            
            return JsonResponse({'success': True, 'message': 'Attendance marked successfully!'})
            
        except (json.JSONDecodeError, KeyError, ValueError):
            return JsonResponse({'success': False, 'message': 'Invalid QR code data.'})
    
    return render(request, 'students/scan_qr.html')


@login_required
def materials_list(request):
    materials = Material.objects.all().order_by('-upload_date')
    return render(request, 'students/materials_list.html', {'materials': materials})


@login_required
def download_material(request, material_id):
    from django.http import HttpResponse
    material = get_object_or_404(Material, id=material_id)
    response = HttpResponse(material.file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{material.file.name}"'
    return response
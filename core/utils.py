import requests
import json
from django.conf import settings
from datetime import datetime, time
import qrcode
import io
import base64
from .models import Attendance


def ai_recommendation(prompt):
    """
    Get AI recommendation from Hugging Face API
    """
    API_URL = "https://api-inference.huggingface.co/models/distilgpt2"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt, "max_length": 100})
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'No recommendation available right now.')
            return "No recommendation available right now."
        else:
            return "AI service temporarily unavailable."
    except Exception as e:
        return "No recommendation available right now."


def get_student_recommendation(student, current_time=None):
    """
    Get personalized recommendation for student based on time and interests
    """
    if current_time is None:
        current_time = datetime.now().time()
    
    # Check if it's a free period (between classes)
    free_periods = [
        (time(9, 30), time(10, 0)),  # 9:30-10:00
        (time(11, 30), time(12, 0)), # 11:30-12:00
        (time(14, 30), time(15, 0)), # 2:30-3:00
    ]
    
    is_free_period = any(start <= current_time <= end for start, end in free_periods)
    
    if is_free_period:
        prompt = f"Suggest a quick 15-minute learning activity for a student interested in {student.interests or 'general studies'}"
    else:
        prompt = f"Suggest a personal development or career skill activity for a student interested in {student.interests or 'technology'}"
    
    return ai_recommendation(prompt)


def generate_qr_code(data):
    """
    Generate QR code and return as base64 string
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def calculate_attendance_percentage(student, subject=None):
    """
    Calculate attendance percentage for a student
    """
    if subject:
        total_classes = Attendance.objects.filter(student=student, subject=subject).count()
        present_classes = Attendance.objects.filter(student=student, subject=subject, is_present=True).count()
    else:
        total_classes = Attendance.objects.filter(student=student).count()
        present_classes = Attendance.objects.filter(student=student, is_present=True).count()
    
    if total_classes == 0:
        return 0.0
    
    return round((present_classes / total_classes) * 100, 2)


def get_weekly_timetable():
    """
    Get hardcoded weekly timetable
    """
    timetable = {
        'Monday': [
            {'time': '09:00', 'subject': 'Mathematics', 'room': 'A101'},
            {'time': '10:00', 'subject': 'Physics', 'room': 'B201'},
            {'time': '11:00', 'subject': 'Chemistry', 'room': 'C301'},
            {'time': '12:00', 'subject': 'English', 'room': 'D401'},
            {'time': '14:00', 'subject': 'Computer Science', 'room': 'E501'},
        ],
        'Tuesday': [
            {'time': '09:00', 'subject': 'Mathematics', 'room': 'A101'},
            {'time': '10:00', 'subject': 'Biology', 'room': 'F601'},
            {'time': '11:00', 'subject': 'History', 'room': 'G701'},
            {'time': '12:00', 'subject': 'Geography', 'room': 'H801'},
            {'time': '14:00', 'subject': 'Physical Education', 'room': 'Gym'},
        ],
        'Wednesday': [
            {'time': '09:00', 'subject': 'Physics', 'room': 'B201'},
            {'time': '10:00', 'subject': 'Chemistry', 'room': 'C301'},
            {'time': '11:00', 'subject': 'Mathematics', 'room': 'A101'},
            {'time': '12:00', 'subject': 'Computer Science', 'room': 'E501'},
            {'time': '14:00', 'subject': 'English', 'room': 'D401'},
        ],
        'Thursday': [
            {'time': '09:00', 'subject': 'Biology', 'room': 'F601'},
            {'time': '10:00', 'subject': 'Mathematics', 'room': 'A101'},
            {'time': '11:00', 'subject': 'Physics', 'room': 'B201'},
            {'time': '12:00', 'subject': 'History', 'room': 'G701'},
            {'time': '14:00', 'subject': 'Chemistry', 'room': 'C301'},
        ],
        'Friday': [
            {'time': '09:00', 'subject': 'Computer Science', 'room': 'E501'},
            {'time': '10:00', 'subject': 'English', 'room': 'D401'},
            {'time': '11:00', 'subject': 'Geography', 'room': 'H801'},
            {'time': '12:00', 'subject': 'Mathematics', 'room': 'A101'},
            {'time': '14:00', 'subject': 'Physical Education', 'room': 'Gym'},
        ],
    }
    return timetable

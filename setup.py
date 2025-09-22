#!/usr/bin/env python
"""
Setup script for SIH Smart Education System
Run this script to set up the project with demo data
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_project():
    """Set up the Django project with migrations and demo data"""
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sih_project.settings')
    django.setup()
    
    print("🚀 Setting up SIH Smart Education System...")
    
    # Run migrations
    print("📦 Running database migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create superuser if it doesn't exist
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        print("👤 Creating admin user...")
        User.objects.create_superuser(
            username='admin',
            email='admin@sih.edu',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("✅ Admin user created: admin / admin123")
    else:
        print("✅ Admin user already exists")
    
    # Set up demo data
    print("🎭 Setting up demo data...")
    execute_from_command_line(['manage.py', 'setup_demo_data'])
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Demo Accounts:")
    print("   Admin: admin / admin123")
    print("   Teacher: teacher1 / password123")
    print("   Student: student1 / password123")
    print("\n🌐 Start the server with: python manage.py runserver")
    print("🔗 Access the application at: http://127.0.0.1:8000")

if __name__ == '__main__':
    setup_project()




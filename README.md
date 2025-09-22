# SIH Smart Education System

A comprehensive Django-based smart education platform for managing attendance, study materials, and AI-powered recommendations.

## Features

### 🎓 Student Features
- **Dashboard**: View attendance, timetable, and AI recommendations
- **QR Code Attendance**: Scan QR codes to mark attendance
- **Study Materials**: Download materials uploaded by teachers
- **AI Recommendations**: Get personalized learning suggestions based on time and interests

### 👨‍🏫 Teacher Features
- **Dashboard**: Manage classes and view attendance reports
- **QR Code Generation**: Create QR codes for attendance marking
- **Material Upload**: Upload study materials (PDFs, documents, presentations)
- **Attendance Reports**: View detailed attendance statistics for students

### 👨‍💼 Admin Features
- **User Management**: Add and manage students and teachers
- **Announcements**: Create and manage system-wide announcements
- **System Overview**: Monitor user statistics and system status

## Tech Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (default)
- **Frontend**: HTML, CSS, Bootstrap 5
- **AI Integration**: Hugging Face Inference API
- **QR Codes**: qrcode library
- **File Handling**: Django's built-in file handling

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sih
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env file with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Set up demo data (optional)**
   ```bash
   python manage.py setup_demo_data
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Demo Accounts

After running `setup_demo_data`, you can use these accounts:

- **Admin**: `admin` / `admin123`
- **Teacher**: `teacher1` / `password123`
- **Student**: `student1` / `password123`

## API Configuration

### Hugging Face API Setup

1. Get your API key from [Hugging Face](https://huggingface.co/settings/tokens)
2. Add it to your `.env` file:
   ```
   HUGGINGFACE_API_KEY=your-api-key-here
   ```

## Project Structure

```
sih/
├── sih_project/          # Django project settings
├── core/                 # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── urls.py           # URL routing
│   ├── admin.py          # Admin interface
│   ├── utils.py          # Utility functions (AI, QR codes)
│   └── management/       # Custom management commands
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS)
├── media/                # Uploaded files
└── requirements.txt      # Python dependencies
```

## Key Models

- **Student**: User profile with attendance and interests
- **Teacher**: User profile with department and subjects
- **Subject**: Course information
- **Attendance**: Attendance records
- **Material**: Study materials uploaded by teachers
- **Announcement**: System announcements
- **QRCode**: QR codes for attendance

## AI Integration

The system uses Hugging Face's DistilGPT-2 model for generating personalized recommendations:

- **Free Period Recommendations**: Quick learning activities during breaks
- **Personal Growth Suggestions**: Career and skill development activities
- **Context-Aware**: Recommendations based on student interests and current time

## QR Code Attendance System

1. **Teacher generates QR code** for a specific subject
2. **QR code expires after 15 minutes** for security
3. **Students scan QR code** using their mobile devices
4. **Attendance is automatically marked** in the database
5. **Real-time updates** to attendance percentages

## File Upload System

- **Supported formats**: PDF, DOC, DOCX, PPT, PPTX, TXT
- **File organization**: By subject and upload date
- **Access control**: Students can only download, teachers can upload
- **File management**: Automatic file handling and storage

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Admin Interface
Access the admin interface at `/admin/` with your superuser credentials.

## Deployment

For production deployment:

1. Set `DEBUG = False` in settings
2. Configure a production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure media file serving
5. Set up proper security settings
6. Use environment variables for sensitive data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is developed for SIH (Smart India Hackathon) 2024.

## Support

For support and questions, please contact the development team or create an issue in the repository.




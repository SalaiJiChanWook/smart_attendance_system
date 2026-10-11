import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.expanduser('~/smart_attendance_system/data/attendance.db'),
    }
}

INSTALLED_APPS = [
    # Django default apps...
    'rest_framework',
    'corsheaders',
    'attendance_api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # Frontend ချိတ်ဆက်ရန်
    'django.middleware.common.CommonMiddleware',
    # Other middlewares...
]

CORS_ALLOW_ALL_ORIGINS = True # React Frontend ချိတ်ဆက်ခွင့်
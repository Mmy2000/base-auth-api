# 🚀 Quick Start Guide - Django Backend

Get your Django authentication API up and running in 5 minutes!

---

## ⚡ Prerequisites

- Python 3.8+
- pip
- Virtual environment (optional but recommended)

---

## 📦 Installation

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd backend
```

### 2. Virtual Environment
```bash
# Create
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Environment Variables
```bash
cp .env.example .env
```

Edit `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# For development - prints emails to console
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 2. Settings Configuration

Add to your `project/settings.py`:

```python
# At the top
from datetime import timedelta

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Email Configuration (Development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@yourapp.com'

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS (if using frontend)
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Your frontend URL
]
```

### 3. Update URLs

In `project/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 🗄️ Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

---

## 🎬 Run Server

```bash
python manage.py runserver
```

**API available at:** http://localhost:8000

---

## ✅ Test It Works

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

### 2. Check Console for OTP
Look in your terminal where Django is running. You'll see an email with a 6-digit OTP.

### 3. Activate Account
```bash
curl -X POST http://localhost:8000/api/accounts/activate/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "otp": 123456
  }'
```

### 4. Login
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

You'll receive JWT tokens in the response!

---

## 🧪 Run Tests

```bash
python manage.py test accounts
```

---

## 📚 Next Steps

1. **Configure Email** - Set up SMTP for production (see docs/SETTINGS_CONFIGURATION.md)
2. **Database** - Switch to PostgreSQL for production
3. **CORS** - Configure allowed origins
4. **API Docs** - Read full API documentation in docs/
5. **Deploy** - Follow deployment guide for production

---

## 🐛 Troubleshooting

### Issue: "AUTH_USER_MODEL not set"
**Solution:** Add `AUTH_USER_MODEL = 'accounts.User'` to settings.py

### Issue: "No module named 'rest_framework'"
**Solution:** Run `pip install -r requirements.txt`

### Issue: "Table doesn't exist"
**Solution:** Run `python manage.py migrate`

### Issue: "CORS errors"
**Solution:** 
1. Install: `pip install django-cors-headers`
2. Add to INSTALLED_APPS: `'corsheaders'`
3. Add to MIDDLEWARE: `'corsheaders.middleware.CorsMiddleware'`
4. Set: `CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]`

---

## 📖 Full Documentation

- **[Complete README](README.md)** - Full project documentation
- **[API Reference](docs/API_DOCUMENTATION.md)** - All endpoints
- **[Settings Guide](docs/SETTINGS_CONFIGURATION.md)** - Detailed configuration
- **[Architecture](docs/PROFILE_SERVICE_REFACTORING.md)** - Code architecture

---

## 🎉 You're Ready!

Your Django authentication API is now running. Start building your frontend or test the API endpoints!

**Need help?** Check the documentation or open an issue.

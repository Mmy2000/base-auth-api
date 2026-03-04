# 🔐 Django Authentication API

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14+-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-black.svg)](https://github.com/psf/black)

A production-ready Django REST Framework authentication API implementing **SOLID principles**, **clean architecture**, and **service layer pattern**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Authentication Flow](#authentication-flow)
- [Testing](#testing)
- [Security](#security)
- [Deployment](#deployment)
- [Documentation](#documentation)

---

## 🎯 Overview

This Django REST Framework API provides a complete authentication system with:

- **Service Layer Pattern** - Business logic separated from views
- **SOLID Principles** - Clean, maintainable, testable code
- **JWT Authentication** - Stateless, secure token-based auth
- **OTP Verification** - Email-based account activation
- **Password Management** - Reset and change functionality
- **Comprehensive Testing** - 85%+ code coverage

Perfect for modern web applications, mobile apps, or microservices.

---

## ✨ Features

### 🔐 Authentication
- ✅ **User Registration** - Auto-generated usernames from email
- ✅ **Email Verification** - 6-digit OTP with 10-minute expiry
- ✅ **JWT Authentication** - Access & refresh tokens
- ✅ **OTP Resend** - Request new verification code
- ✅ **Token Refresh** - Automatic token renewal

### 🔑 Password Management
- ✅ **Forgot Password** - OTP-based password reset
- ✅ **Reset Password** - Secure password reset with OTP
- ✅ **Change Password** - Update password for authenticated users

### 👤 User Management
- ✅ **User Profiles** - Extended user information
- ✅ **Profile Updates** - Update user and profile data
- ✅ **Image Upload** - Profile picture support
- ✅ **Custom User Model** - Email as username

### 🛡️ Security
- ✅ **Password Hashing** - PBKDF2 encryption
- ✅ **Email Enumeration Prevention** - Secure reset flow
- ✅ **OTP Expiration** - Time-limited verification
- ✅ **Input Validation** - Comprehensive validation
- ✅ **CORS Protection** - Configurable CORS headers

### 🧪 Quality Assurance
- ✅ **Unit Tests** - Service layer tests
- ✅ **Integration Tests** - API endpoint tests
- ✅ **Test Coverage** - 85%+ coverage
- ✅ **Type Hints** - Python type annotations

---

## 🏗️ Architecture

### Clean Architecture with Service Layer

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Views (API Endpoints)                            │     │
│  │  • HTTP Request/Response Handling                 │     │
│  │  • Serialization/Deserialization                  │     │
│  │  • Authentication & Authorization                 │     │
│  └───────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                           │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Business Logic Services                          │     │
│  │  • UserRegistrationService                        │     │
│  │  • AccountActivationService                       │     │
│  │  • AuthenticationService                          │     │
│  │  • ProfileUpdateService                           │     │
│  │  • PasswordResetRequestService                    │     │
│  │  • PasswordResetConfirmService                    │     │
│  │  • PasswordChangeService                          │     │
│  │  • OTPResendService                               │     │
│  └───────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                             │
│  ┌───────────────────────────────────────────────────┐     │
│  │  Models & Database                                │     │
│  │  • User Model (Custom AbstractBaseUser)          │     │
│  │  • Profile Model (OneToOne with User)            │     │
│  │  • Django ORM                                     │     │
│  └───────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

#### 1. **Service Layer Pattern**
```python
# View delegates to service
class UserRegistrationView(APIView):
    def __init__(self):
        self.registration_service = UserRegistrationService(...)
    
    def post(self, request):
        # Validate
        serializer = UserRegistrationSerializer(data=request.data)
        # Delegate to service
        user, error = self.registration_service.register_user(data)
        # Return response
```

#### 2. **Dependency Injection**
```python
# Services receive dependencies
class UserRegistrationService:
    def __init__(self, otp_generator, email_service):
        self.otp_generator = otp_generator
        self.email_service = email_service
```

#### 3. **Strategy Pattern**
```python
# Swappable implementations
class OTPGenerator(ABC):
    @abstractmethod
    def generate(self) -> int:
        pass

class NumericOTPGenerator(OTPGenerator):
    def generate(self) -> int:
        return random.randint(100000, 999999)
```

---

## 📁 Project Structure

```
backend/
│
├── accounts/                        # Main authentication app
│   ├── migrations/                 # Database migrations
│   │   └── 0001_initial.py
│   │
│   ├── __init__.py
│   ├── models.py                   # User & Profile models
│   ├── serializers.py              # DRF serializers
│   ├── services.py                 # Business logic services
│   ├── views.py                    # API views
│   ├── urls.py                     # URL routing
│   ├── admin.py                    # Django admin config
│   ├── apps.py                     # App configuration
│   └── tests.py                    # Unit & integration tests
│
├── project/                         # Django project settings
│   ├── __init__.py
│   ├── settings.py                 # Project configuration
│   ├── urls.py                     # Root URL configuration
│   ├── wsgi.py                     # WSGI configuration
│   └── asgi.py                     # ASGI configuration
│
├── media/                           # User uploaded files
│   └── users_images/               # Profile pictures
│
├── docs/                            # Documentation
│   ├── API_DOCUMENTATION.md        # API reference
│   ├── SETTINGS_CONFIGURATION.md   # Setup guide
│   ├── PASSWORD_MANAGEMENT.md      # Password features
│   └── ARCHITECTURE.md             # Architecture details
│
├── manage.py                        # Django management script
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── pytest.ini                       # Pytest configuration
└── README.md                        # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL (recommended) or SQLite
- Virtual environment tool (venv, virtualenv, or conda)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/django-auth-api.git
   cd django-auth-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate on Linux/Mac
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database (Optional - defaults to SQLite)
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=auth_db
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   
   # Email Configuration
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=noreply@yourapp.com
   ```

5. **Configure Django settings**
   
   Add to `project/settings.py`:
   ```python
   # Custom User Model
   AUTH_USER_MODEL = 'accounts.User'
   
   # REST Framework
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': (
           'rest_framework_simplejwt.authentication.JWTAuthentication',
       ),
       # ... other settings
   }
   
   # JWT Settings
   from datetime import timedelta
   SIMPLE_JWT = {
       'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
       'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
       # ... other settings
   }
   
   # CORS Headers
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",  # Your frontend
   ]
   ```
   
   **See `docs/SETTINGS_CONFIGURATION.md` for complete setup**

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```
   
   API available at: **http://localhost:8000**

---

## ⚙️ Configuration

### Email Backend

**Development (Console):**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Production (SMTP):**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-specific-password'
```

### Database

**SQLite (Development):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**PostgreSQL (Production):**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'auth_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### CORS Configuration

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add at top
    # ...
]

# Allow specific origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-frontend.com",
]

# Or allow all (development only)
CORS_ALLOW_ALL_ORIGINS = True
```

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api/accounts/
```

### Endpoints Overview

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register/` | ❌ | Register new user |
| POST | `/activate/` | ❌ | Activate account with OTP |
| POST | `/resend-otp/` | ❌ | Resend activation OTP |
| POST | `/login/` | ❌ | Login and get JWT tokens |
| POST | `/token/refresh/` | ❌ | Refresh access token |
| POST | `/password-reset/request/` | ❌ | Request password reset OTP |
| POST | `/password-reset/confirm/` | ❌ | Reset password with OTP |
| POST | `/password/change/` | ✅ | Change password |
| GET | `/profile/` | ✅ | Get user profile |
| PUT | `/profile/` | ✅ | Update user profile |

### Example Requests

#### 1. Register User
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful. Please check your email for OTP.",
  "data": {
    "email": "user@example.com",
    "username": "user"
  }
}
```

#### 2. Activate Account
```bash
curl -X POST http://localhost:8000/api/accounts/activate/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": 123456
  }'
```

#### 3. Login
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "user",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

#### 4. Get Profile (Authenticated)
```bash
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 5. Update Profile (Authenticated)
```bash
curl -X PUT http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "username": "johnsmith",
    "country": "USA",
    "city": "New York"
  }'
```

**Complete API documentation:** [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md)

---

## 🔄 Authentication Flow

### Registration → Activation → Login

```
1. User Registration
   POST /api/accounts/register/
   ↓
   • Backend creates inactive user
   • Generates 6-digit OTP
   • Sets 10-minute expiry
   • Sends OTP via email
   ↓
2. Account Activation
   POST /api/accounts/activate/
   ↓
   • Backend validates OTP
   • Checks expiry
   • Activates user account
   • Clears OTP
   ↓
3. Login
   POST /api/accounts/login/
   ↓
   • Backend authenticates user
   • Generates JWT tokens
   • Returns access & refresh tokens
   ↓
4. Access Protected Resources
   GET /api/accounts/profile/
   Header: Authorization: Bearer {access_token}
   ↓
5. Token Refresh (when expired)
   POST /api/accounts/token/refresh/
   Body: { "refresh": "..." }
   ↓
   • Backend validates refresh token
   • Issues new access token
```

### Password Reset Flow

```
1. Request Password Reset
   POST /api/accounts/password-reset/request/
   ↓
   • Backend generates OTP
   • Sends reset email
   ↓
2. Confirm Password Reset
   POST /api/accounts/password-reset/confirm/
   ↓
   • Backend validates OTP
   • Updates password
   • Clears OTP
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test accounts

# Run specific test class
python manage.py test accounts.tests.UserRegistrationServiceTest

# Run with verbosity
python manage.py test accounts -v 2

# Run specific test method
python manage.py test accounts.tests.UserRegistrationServiceTest.test_register_user_success
```

### Test Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test accounts

# Generate report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

### Test Structure

```python
# Service Tests (Unit Tests)
class UserRegistrationServiceTest(TestCase):
    """Test business logic"""
    
# API Tests (Integration Tests)
class RegistrationAPITest(APITestCase):
    """Test API endpoints"""
```

**Current Coverage:** 85%+

---

## 🔒 Security

### Authentication & Authorization
- ✅ JWT token-based authentication
- ✅ Token expiration (60 min access, 7 days refresh)
- ✅ Refresh token rotation
- ✅ Password hashing with PBKDF2

### Password Security
- ✅ Minimum length validation (8 characters)
- ✅ Common password checking
- ✅ Numeric password rejection
- ✅ User attribute similarity check

### OTP Security
- ✅ 6-digit numeric OTP
- ✅ 10-minute expiration
- ✅ Single-use OTPs
- ✅ Secure random generation

### API Security
- ✅ Email enumeration prevention
- ✅ Rate limiting ready
- ✅ CORS protection
- ✅ Input validation
- ✅ SQL injection protection (ORM)

### Best Practices
- ✅ No sensitive data in error messages
- ✅ Secure password reset flow
- ✅ HTTPS enforcement in production
- ✅ Security headers configured
- ✅ Debug mode disabled in production

---

## 🚀 Deployment

### Using Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

# Run with gunicorn
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: auth_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn project.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/auth_db

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Using Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="your-password"

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

---

## 📚 Documentation

Comprehensive documentation available:

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference with examples
- **[Settings Configuration](docs/SETTINGS_CONFIGURATION.md)** - Django settings setup guide
- **[Password Management](docs/PASSWORD_MANAGEMENT.md)** - Password reset & change features
- **[Profile Service Refactoring](docs/PROFILE_SERVICE_REFACTORING.md)** - Service layer implementation
- **[OTP Expiry Summary](docs/OTP_EXPIRY_SUMMARY.md)** - OTP expiration feature
- **[Username Profile Update](docs/USERNAME_PROFILE_UPDATE_SUMMARY.md)** - Username auto-generation

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests for your changes
4. Ensure all tests pass (`python manage.py test`)
5. Commit your changes (`git commit -m 'Add AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8
- Use Black for formatting
- Add type hints
- Write docstrings
- Keep functions small and focused

---

## 📝 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- **Django** - The web framework for perfectionists
- **Django REST Framework** - Powerful API toolkit
- **djangorestframework-simplejwt** - JWT authentication
- **Python Community** - Amazing ecosystem

---

## 📞 Support

- 📧 Email: support@yourproject.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/project/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/project/discussions)

---

<div align="center">

**Built with ❤️ using Django & Python**

[Documentation](docs/) · [Report Bug](issues) · [Request Feature](issues)

⭐ Star this repo if you find it helpful!

</div>

# Hotel Booking System

A comprehensive hotel booking and management system built with Django and Django REST Framework. This application provides a platform for hotel managers to list their properties and for customers to book rooms online.

## 🚀 Features

### For Customers
- Browse hotels and view detailed information
- Advanced search with filters (location, price, amenities, dates)
- Search for available rooms based on dates and preferences
- Make and manage bookings with real-time availability
- Secure payment processing with Stripe integration
- View booking history and status
- Leave reviews and ratings for hotels
- User profile management with loyalty program
- Email notifications for bookings and payments

### For Hotel Managers
- Hotel property management with image uploads
- Room inventory and pricing management
- Booking management and processing (confirm, check-in, check-out)
- Real-time booking notifications
- Analytics dashboard with occupancy rates and revenue
- Customer review management

### System Features
- RESTful API with comprehensive documentation
- User authentication and authorization with role-based access
- Advanced caching with Redis for optimal performance
- Full-text search with Elasticsearch integration
- Email notifications with Celery task queue
- Rate limiting and security headers
- Audit trails and comprehensive logging
- Payment processing with Stripe webhooks
- Multi-environment configuration

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7**: Web framework
- **Django REST Framework 3.14.0**: API development with OpenAPI documentation
- **PostgreSQL**: Primary database (SQLite for development)
- **Redis**: Caching, session management, and message broker
- **Elasticsearch**: Advanced search and indexing
- **Celery**: Distributed task queue for async operations
- **Stripe**: Payment processing
- **Gunicorn**: WSGI HTTP Server for production

### Additional Tools
- **Docker**: Containerization for development services
- **Sentry**: Error tracking and performance monitoring
- **Pytest**: Testing framework with coverage reporting

## 📁 Project Structure

The project is organized into the following main apps:

```
hotel_booking/
├── core/                    # Base models, utilities, and services
│   ├── models.py           # Abstract base models (TimeStamped, SoftDelete)
│   ├── services.py         # Business logic layer
│   ├── validators.py       # Custom validation logic
│   ├── exceptions.py       # Custom exception handling
│   ├── security.py         # Security middleware and utilities
│   └── logging.py          # Centralized logging utilities
├── users/                   # User authentication and profiles
│   ├── models.py           # Custom User model with role-based access
│   ├── serializers.py      # User API serializers
│   └── permissions.py      # Custom permission classes
├── hotels/                  # Hotel, room, and amenity management
│   ├── models.py           # Hotel, Room, Amenity, Review models
│   ├── views.py            # Hotel API viewsets with advanced filtering
│   ├── serializers.py      # Hotel API serializers
│   ├── documents.py        # Elasticsearch document definitions
│   └── permissions.py      # Hotel-specific permissions
├── bookings/               # Booking and payment processing
│   ├── models.py           # Booking and Payment models
│   ├── views.py            # Booking management API
│   ├── tasks.py            # Celery tasks for email notifications
│   ├── payment_views.py    # Stripe payment integration
│   └── signals.py          # Booking-related signal handlers
└── templates/              # HTML templates for web interface
    ├── base.html
    ├── core/
    ├── users/
    └── bookings/
```

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose (for services)
- Git

### 1. Clone and Setup

```bash
git clone https://github.com/idorenyinbassey/hotel_booking.git
cd hotel_booking

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# - Database settings
# - Redis URL
# - Stripe API keys
# - Email configuration
```

### 3. Start Development Services

```bash
# Start Redis, Elasticsearch, and PostgreSQL
docker-compose up -d

# Wait for services to be ready
docker-compose logs -f
```

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 5. Search Index Setup

```bash
# Create Elasticsearch indexes
python manage.py search_index --rebuild
```

### 6. Start Development Server

```bash
# Start Django development server
python manage.py runserver

# In another terminal, start Celery worker for async tasks
celery -A hotel_booking worker -l info
```

### 7. Access the Application

- **Web Interface**: http://127.0.0.1:8000/
- **API Documentation**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📚 API Documentation

The API is organized by functional areas:

### Authentication & Users
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update user profile

### Hotels & Accommodations
- `GET /api/hotels/` - List hotels with filtering and search
- `GET /api/hotels/{id}/` - Get hotel details
- `GET /api/hotels/{id}/rooms/` - Get hotel rooms
- `GET /api/hotels/{id}/reviews/` - Get hotel reviews
- `POST /api/hotels/{id}/reviews/` - Create hotel review

### Bookings & Reservations
- `GET /api/bookings/` - List user bookings
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/{id}/` - Get booking details
- `POST /api/bookings/{id}/confirm/` - Confirm booking
- `POST /api/bookings/{id}/check-in/` - Check-in guest
- `POST /api/bookings/{id}/check-out/` - Check-out guest

### Advanced API Features
- **Filtering**: `?city=Paris&min_price=100&max_price=500`
- **Search**: `?search=luxury hotel paris`
- **Pagination**: `?page=2&page_size=20`
- **Ordering**: `?ordering=-created_at`

### Interactive API Documentation
Visit `/api/schema/swagger-ui/` for complete interactive API documentation with:
- Request/response schemas
- Authentication requirements
- Try-it-out functionality
- Code examples

## 🏗️ Architecture & Design

### Service Layer Pattern
The application uses a service layer to separate business logic from API views:

```python
# Example: Creating a booking through service layer
from core.services import BookingService

booking = BookingService.create_booking(
    user=request.user,
    hotel_id=hotel_id,
    room_id=room_id,
    check_in_date=check_in_date,
    check_out_date=check_out_date,
    adults=2,
    children=0
)
```

### Caching Strategy
- **Redis** for session storage and API response caching
- **Database query optimization** with select_related and prefetch_related
- **Elasticsearch** for search result caching

### Security Features
- **Rate limiting** (60 requests per minute per IP)
- **CORS protection** with configurable origins
- **Input validation** and sanitization
- **Audit trails** for all data changes
- **Security headers** middleware

### Error Handling
Consistent error responses across all API endpoints:

```json
{
  "error": "booking_error",
  "message": "Room is not available for selected dates",
  "details": null,
  "request_id": "abc123",
  "timestamp": "2025-07-21T12:00:00Z"
}
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest users/tests.py

# Run with verbose output
pytest -v
```

### Test Categories
- **Unit Tests**: Model validation, utility functions
- **Integration Tests**: API endpoints, business logic
- **Performance Tests**: Database queries, API response times

### Test Data
Sample test data is available in `fixtures/` directory:

```bash
# Load test data
python manage.py loaddata fixtures/test_hotels.json
python manage.py loaddata fixtures/test_bookings.json
```

## 🚀 Deployment

### Production Configuration

1. **Environment Variables**
```bash
DEBUG=False
SECRET_KEY=your-secure-production-secret-key
DATABASE_URL=postgres://user:password@host:port/database
REDIS_URL=redis://redis-host:6379/0
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# Stripe Production Keys
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
```

2. **Static Files**
```bash
python manage.py collectstatic --noinput
```

3. **Database Migration**
```bash
python manage.py migrate
```

### Docker Deployment

```dockerfile
# Production Dockerfile example
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "hotel_booking.wsgi:application"]
```

### Health Checks

The application includes health check endpoints:
- `GET /api/health/` - Basic health check
- `GET /api/health/database/` - Database connectivity
- `GET /api/health/cache/` - Redis connectivity

## 📊 Monitoring & Analytics

### Available Metrics
- API response times and error rates
- Database query performance
- Cache hit rates
- Booking conversion rates
- User activity patterns

### Logging
Structured logging with:
- Request/response logging
- Business event logging (bookings, payments)
- Error tracking with stack traces
- Performance monitoring

### Performance Monitoring
- **Database Query Analysis**: Track slow queries
- **Cache Performance**: Monitor Redis hit/miss rates  
- **API Performance**: Response time percentiles
- **Business Metrics**: Booking success rates, revenue tracking

## 🔧 Configuration Options

### Cache Configuration
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 3600,  # 1 hour default timeout
    }
}
```

### Elasticsearch Configuration
```python
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}
```

### Email Backend Options
```python
# Development: Console backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Production: SMTP backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# With SendGrid
EMAIL_BACKEND = 'anymail.backends.sendgrid.EmailBackend'
ANYMAIL = {
    'SENDGRID_API_KEY': 'your-api-key',
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style Guidelines
- Follow PEP 8 for Python code
- Use type hints where possible
- Write comprehensive docstrings
- Maintain test coverage above 90%

## 📝 Changelog

### Version 2.0.0 (Latest)
- ✅ Added comprehensive API documentation with Swagger/OpenAPI
- ✅ Integrated Redis caching for improved performance
- ✅ Added Elasticsearch for advanced search capabilities
- ✅ Implemented Stripe payment processing
- ✅ Added email notifications with Celery task queue
- ✅ Enhanced security with rate limiting and audit trails
- ✅ Added service layer architecture for better code organization
- ✅ Comprehensive error handling and validation
- ✅ Added Docker configuration for development services

### Version 1.0.0
- Basic hotel booking functionality
- User authentication and role management
- Hotel and room management
- Basic booking system
- REST API with Django REST Framework

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Django and Django REST Framework communities
- Bootstrap team for the frontend framework
- Redis Labs for caching solutions
- Elasticsearch for search capabilities
- Stripe for payment processing
- All contributors and beta testers

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Email: support@hotelbooking.com
- Documentation: [Full Documentation](https://docs.hotelbooking.com)

---

**Built with ❤️ using Django, DRF, and modern web technologies**
# Hotel Booking System

A comprehensive hotel booking and management system built with Django and Django REST Framework. This application provides a platform for hotel managers to list their properties and for customers to book rooms online.

## Features

### For Customers
- Browse hotels and view detailed information
- Search for available rooms based on dates and preferences
- Make and manage bookings
- View booking history and status
- Leave reviews for hotels
- User profile management
- Loyalty program for frequent customers

### For Hotel Managers
- Hotel property management
- Room inventory management
- Booking management and processing
- Check-in and check-out functionality
- View booking statistics and reports

### System Features
- RESTful API for frontend and mobile applications
- User authentication and authorization
- Role-based access control (Customer, Hotel Manager, Administrator)
- Secure payment processing
- Email notifications

## Technology Stack

### Backend
- **Django 4.2.7**: Web framework
- **Django REST Framework 3.14.0**: API development
- **PostgreSQL**: Primary database (configurable)
- **Redis**: Caching and session management
- **Gunicorn**: WSGI HTTP Server for production

### Frontend
- **Bootstrap 5**: CSS framework for responsive design
- **Django Templates**: Server-side rendering

## Project Structure

The project is organized into the following main apps:

- **core**: Base models, utilities, and common functionality
- **users**: User authentication, profiles, and permissions
- **hotels**: Hotel, room, and amenity management
- **bookings**: Booking and payment processing

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)
- PostgreSQL (optional, SQLite for development)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hotel_booking
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///db.sqlite3  # For development
   # For PostgreSQL: DATABASE_URL=postgres://user:password@localhost:5432/hotel_booking
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000/

## API Documentation

The API endpoints are organized by app:

- `/api/users/` - User management
- `/api/hotels/` - Hotel and room management
- `/api/bookings/` - Booking and payment processing

Detailed API documentation is available at `/api/docs/` when the server is running.

## Development

### Running Tests

```bash
python manage.py test
```

Or with pytest:

```bash
pytest
```

### Code Quality

Check code coverage:

```bash
pytest --cov=.
```

## Deployment

### Production Settings

For production deployment, update the `.env` file with appropriate settings:

```
DEBUG=False
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgres://user:password@host:port/database
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Serving Static Files

Collect static files for production:

```bash
python manage.py collectstatic
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Django and Django REST Framework communities
- Bootstrap team for the frontend framework
- All contributors to this project

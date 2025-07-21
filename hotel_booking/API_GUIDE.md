# 📚 Hotel Booking System - API Documentation Guide

This comprehensive guide covers all API endpoints, authentication methods, and usage examples for the Hotel Booking System.

## 🔗 Base URL
```
http://localhost:8000/api/
```

## 🔑 Authentication

The API uses Token-based authentication. Include the token in the Authorization header:

```http
Authorization: Token your-auth-token-here
```

### Obtaining a Token

**Login Endpoint:**
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "your-password"
}
```

**Response:**
```json
{
    "key": "your-auth-token-here",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    }
}
```

## 👥 User Management

### User Registration
```http
POST /api/auth/registration/
Content-Type: application/json

{
    "email": "newuser@example.com",
    "password1": "securepassword123",
    "password2": "securepassword123",
    "first_name": "Jane",
    "last_name": "Smith"
}
```

### User Profile
```http
GET /api/auth/user/
Authorization: Token your-auth-token-here
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "date_joined": "2025-07-21T10:30:00Z"
}
```

### Update Profile
```http
PUT /api/auth/user/
Authorization: Token your-auth-token-here
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Updated",
    "phone": "+1234567890"
}
```

## 🏨 Hotels API

### List Hotels
```http
GET /api/hotels/
```

**Query Parameters:**
- `search`: Search by hotel name or description
- `city`: Filter by city
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `amenities`: Filter by amenities (comma-separated)
- `ordering`: Sort by `name`, `price`, `-created_at`

**Example:**
```http
GET /api/hotels/?search=luxury&city=New York&min_price=100&max_price=500
```

**Response:**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/hotels/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Luxury Hotel NYC",
            "description": "Premium hotel in Manhattan",
            "address": "123 5th Avenue, New York, NY",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "zip_code": "10001",
            "phone": "+1-212-555-0123",
            "email": "info@luxuryhotelnyc.com",
            "website": "https://luxuryhotelnyc.com",
            "star_rating": 5,
            "amenities": ["WiFi", "Pool", "Gym", "Spa"],
            "images": [
                "http://localhost:8000/media/hotels/luxury-hotel-1.jpg"
            ],
            "average_rating": 4.5,
            "total_reviews": 128,
            "rooms_available": 15,
            "created_at": "2025-07-15T08:30:00Z"
        }
    ]
}
```

### Hotel Details
```http
GET /api/hotels/{hotel_id}/
```

### Hotel Rooms
```http
GET /api/hotels/{hotel_id}/rooms/
```

**Query Parameters:**
- `check_in`: Check-in date (YYYY-MM-DD)
- `check_out`: Check-out date (YYYY-MM-DD)
- `guests`: Number of guests
- `room_type`: Filter by room type

## 🛏️ Rooms API

### List All Rooms
```http
GET /api/rooms/
```

### Room Details
```http
GET /api/rooms/{room_id}/
```

**Response:**
```json
{
    "id": 1,
    "hotel": {
        "id": 1,
        "name": "Luxury Hotel NYC"
    },
    "name": "Deluxe King Room",
    "description": "Spacious room with city view",
    "room_type": "deluxe",
    "max_guests": 2,
    "price_per_night": "299.00",
    "amenities": ["King Bed", "City View", "Mini Bar"],
    "images": [
        "http://localhost:8000/media/rooms/deluxe-king-1.jpg"
    ],
    "is_available": true,
    "created_at": "2025-07-15T08:30:00Z"
}
```

### Check Room Availability
```http
GET /api/rooms/{room_id}/availability/
?check_in=2025-08-01&check_out=2025-08-05
```

## 📅 Bookings API

### Create Booking
```http
POST /api/bookings/
Authorization: Token your-auth-token-here
Content-Type: application/json

{
    "room": 1,
    "check_in": "2025-08-01",
    "check_out": "2025-08-05",
    "guests": 2,
    "special_requests": "High floor room preferred"
}
```

**Response:**
```json
{
    "id": 123,
    "booking_reference": "HB-2025-000123",
    "room": {
        "id": 1,
        "name": "Deluxe King Room",
        "hotel": {
            "id": 1,
            "name": "Luxury Hotel NYC"
        }
    },
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "check_in": "2025-08-01",
    "check_out": "2025-08-05",
    "guests": 2,
    "total_amount": "1196.00",
    "status": "confirmed",
    "special_requests": "High floor room preferred",
    "created_at": "2025-07-21T14:30:00Z"
}
```

### List User Bookings
```http
GET /api/bookings/
Authorization: Token your-auth-token-here
```

**Query Parameters:**
- `status`: Filter by status (`pending`, `confirmed`, `cancelled`)
- `ordering`: Sort by `created_at`, `-created_at`, `check_in`

### Booking Details
```http
GET /api/bookings/{booking_id}/
Authorization: Token your-auth-token-here
```

### Cancel Booking
```http
PATCH /api/bookings/{booking_id}/
Authorization: Token your-auth-token-here
Content-Type: application/json

{
    "status": "cancelled"
}
```

## 💳 Payment API

### Process Payment
```http
POST /api/payments/process/
Authorization: Token your-auth-token-here
Content-Type: application/json

{
    "booking_id": 123,
    "payment_method_id": "pm_1234567890",
    "amount": "1196.00"
}
```

**Response:**
```json
{
    "payment_intent_id": "pi_1234567890",
    "client_secret": "pi_1234567890_secret_abc123",
    "status": "requires_confirmation",
    "amount": "1196.00",
    "currency": "usd"
}
```

### Payment Webhook (Stripe)
```http
POST /api/payments/stripe/webhook/
Content-Type: application/json
Stripe-Signature: stripe-signature-header

{
    "id": "evt_1234567890",
    "object": "event",
    "type": "payment_intent.succeeded",
    "data": {
        "object": {
            "id": "pi_1234567890",
            "status": "succeeded"
        }
    }
}
```

## 🔍 Search API

### Advanced Hotel Search
```http
GET /api/search/hotels/
```

**Query Parameters:**
- `q`: Search query
- `location`: Location (city, address)
- `check_in`: Check-in date
- `check_out`: Check-out date
- `guests`: Number of guests
- `min_price`: Minimum price
- `max_price`: Maximum price
- `star_rating`: Minimum star rating
- `amenities`: Amenities (comma-separated)
- `sort_by`: Sort by `price`, `rating`, `distance`

### Search Suggestions
```http
GET /api/search/suggestions/?q=new york
```

**Response:**
```json
{
    "hotels": [
        {
            "id": 1,
            "name": "Luxury Hotel NYC",
            "city": "New York"
        }
    ],
    "locations": [
        {
            "city": "New York",
            "state": "NY",
            "country": "USA"
        }
    ]
}
```

## 📊 Analytics API (Admin Only)

### Booking Statistics
```http
GET /api/analytics/bookings/
Authorization: Token admin-token-here
```

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `hotel_id`: Filter by specific hotel

### Revenue Report
```http
GET /api/analytics/revenue/
Authorization: Token admin-token-here
```

## 🔧 API Features

### Pagination
All list endpoints support pagination:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/hotels/?page=2",
    "previous": null,
    "results": [...]
}
```

### Filtering & Searching
Use query parameters for filtering:
- Date ranges: `start_date`, `end_date`
- Text search: `search`, `q`
- Exact matches: `field_name=value`
- Range filters: `min_price`, `max_price`

### Ordering
Use the `ordering` parameter:
- Ascending: `ordering=field_name`
- Descending: `ordering=-field_name`
- Multiple fields: `ordering=field1,-field2`

### Error Handling
Standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Server Error

**Error Response Format:**
```json
{
    "error": "Error description",
    "details": {
        "field_name": ["Field-specific error message"]
    },
    "code": "ERROR_CODE"
}
```

## 📝 Rate Limiting

API endpoints are rate-limited:
- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour
- **Admin users**: 5000 requests/hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1627849200
```

## 🌐 API Versioning

The API uses URL versioning:
- Current version: `v1`
- Base URL: `/api/v1/`

## 📖 Interactive Documentation

Access interactive API documentation:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## 💡 Best Practices

### Authentication
- Always include the Authorization header for protected endpoints
- Store tokens securely
- Handle token expiration gracefully

### Error Handling
```javascript
try {
    const response = await fetch('/api/hotels/', {
        headers: {
            'Authorization': 'Token your-token-here',
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'API request failed');
    }
    
    const data = await response.json();
    return data;
} catch (error) {
    console.error('API Error:', error.message);
}
```

### Pagination
```javascript
async function fetchAllHotels() {
    let allHotels = [];
    let url = '/api/hotels/';
    
    while (url) {
        const response = await fetch(url);
        const data = await response.json();
        allHotels.push(...data.results);
        url = data.next;
    }
    
    return allHotels;
}
```

---

## 🤝 Support

For API support and questions:
- **Email**: support@hotelbooking.com
- **Documentation**: [API Docs](http://localhost:8000/api/docs/)
- **GitHub**: [Hotel Booking Repository](https://github.com/idorenyinbassey/hotel_booking)

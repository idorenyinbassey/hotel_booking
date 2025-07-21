# Users App

The Users app handles user authentication, registration, and profile management for the Hotel Booking system.

## Features

- Custom User model with email as the username field
- User types: Customer, Hotel Manager, Administrator
- User profiles with extended information
- API endpoints for user management
- Frontend views for authentication and profile management
- Password reset functionality

## Models

### User

A custom User model that extends Django's AbstractUser and uses email as the username field.

**Fields:**
- email: Email address (used as username)
- phone_number: User's phone number
- address: User's address
- profile_picture: User's profile picture
- user_type: Type of user (customer, hotel_manager, admin)
- hotel: Foreign key to Hotel model (for hotel managers)

### UserProfile

Extended profile information for users.

**Fields:**
- user: One-to-one relationship with User
- date_of_birth: User's date of birth
- bio: User's biography
- preferences: JSON field for user preferences
- loyalty_points: Points earned in loyalty program
- loyalty_level: Level in loyalty program

## API Endpoints

- `/api/users/`: List and create users
- `/api/users/{id}/`: Retrieve, update, and delete users
- `/api/users/me/`: Retrieve the authenticated user's details
- `/api/users/{id}/profile/`: Update the user's profile
- `/api/users/change-password/`: Change the user's password
- `/api/register/`: Register a new user

## Frontend Views

- `/users/login/`: User login
- `/users/logout/`: User logout
- `/users/register/`: User registration
- `/users/profile/`: User profile
- `/users/profile/update/`: Update personal information
- `/users/profile/update-profile/`: Update profile information
- `/users/profile/change-password/`: Change password
- `/users/password-reset/`: Password reset

## Forms

- CustomUserCreationForm: Form for user registration
- CustomUserChangeForm: Form for updating users
- CustomAuthenticationForm: Form for user login
- UserProfileForm: Form for updating user profiles
- CustomPasswordChangeForm: Form for changing password
- CustomPasswordResetForm: Form for resetting password
- CustomSetPasswordForm: Form for setting a new password

## Templates

- `login.html`: Login page
- `register.html`: Registration page
- `profile.html`: User profile page
- `password_reset.html`: Password reset request page
- `password_reset_confirm.html`: Set new password page
- `password_reset_done.html`: Password reset email sent page
- `password_reset_complete.html`: Password reset complete page
- `password_reset_email.html`: Password reset email template
- `password_reset_subject.txt`: Password reset email subject template

## Template Tags

- `add_class`: Add a CSS class to a form field
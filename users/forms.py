from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Form for user registration."""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'user_type')


class CustomUserChangeForm(UserChangeForm):
    """Form for updating users."""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'address', 'profile_picture', 'user_type')


class CustomAuthenticationForm(AuthenticationForm):
    """Form for user login."""
    
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))


class UserProfileForm(forms.ModelForm):
    """Form for updating user profiles."""
    
    class Meta:
        model = UserProfile
        fields = ('date_of_birth', 'bio', 'preferences')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'preferences': forms.Textarea(attrs={'rows': 3}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Form for changing password."""
    pass


class CustomPasswordResetForm(PasswordResetForm):
    """Form for resetting password."""
    pass


class CustomSetPasswordForm(SetPasswordForm):
    """Form for setting a new password."""
    pass
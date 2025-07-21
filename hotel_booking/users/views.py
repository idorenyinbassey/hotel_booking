from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer, UserRegistrationSerializer, PasswordChangeSerializer
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserProfileForm, CustomPasswordChangeForm

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Allow users to create their own account, but require authentication for other actions.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Regular users can only see their own profile.
        Staff users can see all profiles.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Return the authenticated user's details.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put', 'patch'])
    def profile(self, request, pk=None):
        """
        Update the user's profile.
        """
        user = self.get_object()
        profile = user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change the user's password.
        """
        user = request.user
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"status": "password changed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


# Frontend views
def register(request):
    """
    View for user registration.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """
    View for user profile.
    """
    user_form = CustomUserChangeForm(instance=request.user)
    profile_form = UserProfileForm(instance=request.user.profile)
    password_form = CustomPasswordChangeForm(user=request.user)
    
    # Get user's bookings if they are a customer
    bookings = None
    if request.user.is_customer():
        bookings = request.user.bookings.all().order_by('-created_at')
    
    # Get active bookings count if they are a hotel manager
    active_bookings_count = 0
    if request.user.is_hotel_manager() and request.user.hotel:
        active_bookings_count = request.user.hotel.bookings.filter(
            status__in=['confirmed', 'checked_in']
        ).count()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'bookings': bookings,
        'active_bookings_count': active_bookings_count,
    }
    return render(request, 'users/profile.html', context)


@login_required
def update_personal_info(request):
    """
    View for updating personal information.
    """
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your personal information has been updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('profile')


@login_required
def update_profile(request):
    """
    View for updating profile information.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('profile')


@login_required
def change_password(request):
    """
    View for changing password.
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password has been updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('profile')
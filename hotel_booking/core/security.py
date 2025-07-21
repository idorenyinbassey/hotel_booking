from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
import time
import hashlib


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware to prevent abuse."""
    
    def process_request(self, request):
        # Skip rate limiting for authenticated staff users
        if request.user.is_authenticated and request.user.is_staff:
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Create cache key
        cache_key = f"rate_limit_{ip}"
        
        # Get current request count and timestamp
        request_data = cache.get(cache_key, {'count': 0, 'start_time': time.time()})
        
        # Reset if more than 1 minute has passed
        if time.time() - request_data['start_time'] > 60:
            request_data = {'count': 1, 'start_time': time.time()}
        else:
            request_data['count'] += 1
        
        # Check if rate limit exceeded (60 requests per minute)
        if request_data['count'] > 60:
            return HttpResponseForbidden("Rate limit exceeded")
        
        # Update cache
        cache.set(cache_key, request_data, 60)
        
        return None
    
    def get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to responses."""
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add CSP header for HTML responses
        if response.get('Content-Type', '').startswith('text/html'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' cdnjs.cloudflare.com;"
            )
        
        return response


def hash_sensitive_data(data):
    """Hash sensitive data for logging or storage."""
    return hashlib.sha256(str(data).encode()).hexdigest()[:10]


def sanitize_user_input(input_string):
    """Basic sanitization of user input."""
    import html
    import re
    
    # HTML escape
    sanitized = html.escape(input_string)
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', sanitized)
    
    return sanitized.strip()


class AuditMixin:
    """Mixin to add audit trail to models."""
    
    def save(self, *args, **kwargs):
        # Log model changes
        if hasattr(self, 'pk') and self.pk:
            action = 'UPDATE'
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                changes = self.get_field_changes(old_instance)
            except self.__class__.DoesNotExist:
                changes = {}
        else:
            action = 'CREATE'
            changes = {}
        
        super().save(*args, **kwargs)
        
        # Log the action (implement your logging here)
        self.log_audit_event(action, changes)
    
    def delete(self, *args, **kwargs):
        # Log deletion
        self.log_audit_event('DELETE', {})
        super().delete(*args, **kwargs)
    
    def get_field_changes(self, old_instance):
        """Compare field values to detect changes."""
        changes = {}
        for field in self._meta.fields:
            field_name = field.name
            old_value = getattr(old_instance, field_name)
            new_value = getattr(self, field_name)
            
            if old_value != new_value:
                # Hash sensitive fields
                if field_name in ['password', 'email', 'phone_number']:
                    changes[field_name] = {
                        'old': hash_sensitive_data(old_value),
                        'new': hash_sensitive_data(new_value)
                    }
                else:
                    changes[field_name] = {
                        'old': old_value,
                        'new': new_value
                    }
        
        return changes
    
    def log_audit_event(self, action, changes):
        """Log audit event (implement based on your logging system)."""
        from core.logging import logger
        
        logger.info(
            f"Audit: {action} on {self.__class__.__name__}",
            extra={
                'model': self.__class__.__name__,
                'instance_id': getattr(self, 'pk', None),
                'action': action,
                'changes': changes
            }
        )

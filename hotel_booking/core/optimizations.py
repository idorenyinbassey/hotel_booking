from django.db import models
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class CachedQuerySetMixin:
    """Mixin to add caching capabilities to QuerySets."""
    
    def cached(self, timeout=3600, key_prefix=''):
        """
        Cache the queryset results.
        
        Args:
            timeout: Cache timeout in seconds (default: 1 hour)
            key_prefix: Optional prefix for cache key
        """
        cache_key = f"{key_prefix}{self.model.__name__}_{hash(str(self.query))}"
        
        result = cache.get(cache_key)
        if result is None:
            result = list(self)
            cache.set(cache_key, result, timeout)
        
        return result


class OptimizedHotelQuerySet(models.QuerySet, CachedQuerySetMixin):
    """Optimized queryset for Hotel model."""
    
    def with_related(self):
        """Prefetch related objects to reduce database queries."""
        return self.select_related(
            'location'
        ).prefetch_related(
            'amenities',
            'images',
            'room_types__amenities',
            'room_types__images',
            'reviews__user'
        )
    
    def active(self):
        """Filter only active hotels."""
        return self.filter(is_active=True, is_deleted=False)
    
    def featured(self):
        """Filter only featured hotels."""
        return self.filter(featured=True)
    
    def by_location(self, city=None, country=None):
        """Filter hotels by location."""
        qs = self
        if city:
            qs = qs.filter(location__city__icontains=city)
        if country:
            qs = qs.filter(location__country__icontains=country)
        return qs
    
    def price_range(self, min_price=None, max_price=None):
        """Filter hotels by room price range."""
        qs = self
        if min_price:
            qs = qs.filter(room_types__base_price__gte=min_price)
        if max_price:
            qs = qs.filter(room_types__base_price__lte=max_price)
        return qs.distinct()
    
    def with_amenities(self, amenity_ids):
        """Filter hotels that have specified amenities."""
        return self.filter(amenities__id__in=amenity_ids).distinct()


class OptimizedBookingQuerySet(models.QuerySet, CachedQuerySetMixin):
    """Optimized queryset for Booking model."""
    
    def with_related(self):
        """Prefetch related objects."""
        return self.select_related(
            'user', 'hotel', 'room', 'room__room_type'
        ).prefetch_related('payments')
    
    def upcoming(self):
        """Filter upcoming bookings."""
        from django.utils import timezone
        return self.filter(
            check_in_date__gt=timezone.now().date(),
            status__in=[
                'confirmed', 'pending'
            ]
        )
    
    def active(self):
        """Filter currently active bookings."""
        from django.utils import timezone
        today = timezone.now().date()
        return self.filter(
            check_in_date__lte=today,
            check_out_date__gte=today,
            status='checked_in'
        )
    
    def for_hotel(self, hotel):
        """Filter bookings for a specific hotel."""
        return self.filter(hotel=hotel)
    
    def for_user(self, user):
        """Filter bookings for a specific user."""
        return self.filter(user=user)


# Cache invalidation signals
@receiver([post_save, post_delete])
def invalidate_cache(sender, **kwargs):
    """Invalidate related cache when models change."""
    model_name = sender.__name__
    
    # Clear model-specific cache patterns
    cache_patterns = [
        f"{model_name}_*",
    ]
    
    # Add related model patterns
    if model_name == 'Hotel':
        cache_patterns.extend([
            'hotel_list_*',
            'hotel_detail_*',
            'featured_hotels_*'
        ])
    elif model_name == 'Booking':
        cache_patterns.extend([
            'user_bookings_*',
            'hotel_bookings_*'
        ])
    
    # In production, use more sophisticated cache invalidation
    # For now, we'll use a simple approach
    for pattern in cache_patterns:
        cache.delete_many(cache.keys(pattern))

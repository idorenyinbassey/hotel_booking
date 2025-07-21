from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Hotel


@registry.register_document
class HotelDocument(Document):
    """Elasticsearch document for Hotel model."""
    
    location = fields.ObjectField(properties={
        'city': fields.TextField(),
        'country': fields.TextField(),
        'address': fields.TextField(),
        'latitude': fields.FloatField(),
        'longitude': fields.FloatField(),
    })
    
    amenities = fields.NestedField(properties={
        'name': fields.TextField(),
        'description': fields.TextField(),
    })
    
    room_types = fields.NestedField(properties={
        'name': fields.TextField(),
        'description': fields.TextField(),
        'base_price': fields.FloatField(),
        'max_occupancy': fields.IntegerField(),
    })
    
    average_rating = fields.FloatField()
    
    class Index:
        name = 'hotels'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
    
    class Django:
        model = Hotel
        fields = [
            'id',
            'name',
            'description',
            'star_rating',
            'is_active',
            'featured',
            'created_at',
        ]
        
        related_models = ['location', 'amenities', 'room_types']
    
    def get_queryset(self):
        """Return the queryset that should be indexed."""
        return super().get_queryset().select_related('location').prefetch_related(
            'amenities', 'room_types'
        ).filter(is_active=True)
    
    def get_instances_from_related(self, related_instance):
        """Update hotel document when related objects change."""
        if isinstance(related_instance, Hotel.location.related.related_model):
            return related_instance.hotel
        elif isinstance(related_instance, Hotel.amenities.related.related_model):
            return related_instance.hotels.all()
        elif isinstance(related_instance, Hotel.room_types.related.related_model):
            return related_instance.hotel

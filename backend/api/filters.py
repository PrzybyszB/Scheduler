from django_filters import rest_framework as filters
from .models import Stop

class StopFilter(filters.FilterSet):
    '''
    I create own filter to search exactly stop_id
    '''
    stop_id = filters.CharFilter(field_name='stop_id', lookup_expr='exact')

    class Meta:
        model = Stop
        fields = ['stop_id']

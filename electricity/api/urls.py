from django.urls import path
from .views import RoomLatestReadingListView, MeterReadingBulkCreateView, RoomsConsumptionView

app_name = 'electricity_api'

urlpatterns = [
    path('latest/', RoomLatestReadingListView.as_view(), name='latest-readings'),
    path('add/', MeterReadingBulkCreateView.as_view(), name='add-readings'),
    path('consumption/', RoomsConsumptionView.as_view(), name='electric-consumption'),
]

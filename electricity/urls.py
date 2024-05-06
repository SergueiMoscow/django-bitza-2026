from django.urls import path

from electricity.views import InputCounterDataView, MeterReadingView, Consumption

app_name = 'electricity'

urlpatterns = [
    path('input', InputCounterDataView.as_view(), name='electricity_rooms'),
    path('room/<str:room>', MeterReadingView.as_view(), name='electricity_input'),
    path('consumption', Consumption.as_view(), name='electricity_consumption'),
]

from django.urls import path

from gas.api.views import GasRecordListCreateAPIView, GasRecordDetailAPIView

app_name = 'gas_api'

urlpatterns = [
    path('records/', GasRecordListCreateAPIView.as_view(), name='records'),
    path('records/<int:pk>/', GasRecordDetailAPIView.as_view(), name='record-detail'),
]

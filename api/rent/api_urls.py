from django.urls import path

from api.rent.views import RoomDebtListAPIView, RoomPaymentsAPIView

# from . import api_views

app_name = 'rent_api'

urlpatterns = [
    # path('summary/', api_views.SummaryAPIView.as_view(), name='summary'),
    # path('clients/', api_views.ClientListAPIView.as_view(), name='clients'),
    # path('payments/', api_views.PaymentListAPIView.as_view(), name='payments'),
    # path('contracts/', api_views.ContractListAPIView.as_view(), name='contracts'),
    # path('contacts/list/', api_views.query_contacts, name='query_contacts'),
    # path('payments/new/', api_views.NewPaymentAPIView.as_view(), name='new_payment'),
    # path('close_contract/', api_views.CloseContractAPIView.as_view(), name='close_contract'),
    # Дополнительные маршруты API
    path('summary/', RoomDebtListAPIView.as_view(), name='api_rooms'),
    path('rooms/<str:room_id>/payments/', RoomPaymentsAPIView.as_view(), name='api_room_payments'),
    # path('api/rooms/<str:room_name>/add_payment/', AddPaymentAPIView.as_view(), name='api_add_payment'),
]
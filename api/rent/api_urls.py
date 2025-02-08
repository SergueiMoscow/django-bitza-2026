from django.urls import path

from api.rent.generate_contract_pdf import GenerateContractPDFView
from api.rent.views import RoomDebtListAPIView, RoomPaymentsAPIView, PrintContractsView, ContractPrintCreateView

# from . import api_views

app_name = 'rent_api'

urlpatterns = [
    path('summary/', RoomDebtListAPIView.as_view(), name='api_rooms'),
    path('rooms/<str:room_id>/payments/', RoomPaymentsAPIView.as_view(), name='api_room_payments'),
    path('generate-contract-pdf/', GenerateContractPDFView.as_view(), name='generate-contract-pdf'),
    path('print-contracts/add/', ContractPrintCreateView.as_view(), name='add-contract-print'),
    path('print-contracts/', PrintContractsView.as_view(), name='active-contracts'),

]
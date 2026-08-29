from django.urls import path

from api.rent.generate_contract_pdf import GenerateContractPDFView
from api.rent.views import RoomDebtListAPIView, RoomPaymentsAPIView, PrintContractsView, ContractPrintCreateView, \
    ContactListCreateAPIView, ContactDetailAPIView, ContactDocumentListCreateAPIView, DocumentDetailAPIView, \
    BuildingListCreateAPIView, BuildingDetailAPIView, RoomListCreateAPIView, RoomDetailAPIView, \
    ContractListCreateAPIView, ContractDetailAPIView, PaymentFieldSuggestionsView, PaymentListAPIView
from api.rent.voice import VoiceCommandView, VoiceTranscribeView

# from . import api_views

app_name = 'rent_api'

urlpatterns = [
    path('summary/', RoomDebtListAPIView.as_view(), name='api_rooms'),
    path('rooms/<str:room_id>/payments/', RoomPaymentsAPIView.as_view(), name='api_room_payments'),
    path('payments/', PaymentListAPIView.as_view(), name='payments'),
    path('payments/field-suggestions/', PaymentFieldSuggestionsView.as_view(), name='payment-field-suggestions'),
    path('generate-contract-pdf/', GenerateContractPDFView.as_view(), name='generate-contract-pdf'),
    path('print-contracts/add/', ContractPrintCreateView.as_view(), name='add-contract-print'),
    path('print-contracts/', PrintContractsView.as_view(), name='active-contracts'),
    path('contacts/', ContactListCreateAPIView.as_view(), name='contacts'),
    path('contacts/<int:pk>/', ContactDetailAPIView.as_view(), name='contact-detail'),
    path('contacts/<int:contact_id>/documents/', ContactDocumentListCreateAPIView.as_view(), name='contact-documents'),
    path('documents/<int:pk>/', DocumentDetailAPIView.as_view(), name='document-detail'),
    path('buildings/', BuildingListCreateAPIView.as_view(), name='buildings'),
    path('buildings/<int:pk>/', BuildingDetailAPIView.as_view(), name='building-detail'),
    path('rooms/', RoomListCreateAPIView.as_view(), name='rooms'),
    path('rooms/<str:shortname>/', RoomDetailAPIView.as_view(), name='room-detail'),
    path('contracts/', ContractListCreateAPIView.as_view(), name='contracts'),
    path('contracts/<str:number>/', ContractDetailAPIView.as_view(), name='contract-detail'),
    path('voice-command/', VoiceCommandView.as_view(), name='voice-command'),
    path('voice-transcribe/', VoiceTranscribeView.as_view(), name='voice-transcribe'),

]

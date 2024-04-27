from django.urls import path, re_path

from rent import views, mobile_views
from rent.controllers.ContactView import ContactListView
from rent.controllers.ContractView import ContractListView
from rent.controllers.PaymentView import PaymentListView
from rent.mobile_views import refresh_list_rooms

app_name = 'rent'

urlpatterns = [
    path('summary', views.summary, name='summary'),
    path('clients', ContactListView.as_view(), name='clients'),
    path('payments', PaymentListView.as_view(), name='payments'),
    path('contracts', ContractListView.as_view(), name='contracts'),
    re_path(r'contacts/list', views.query_contacts, name='query_contacts'),
    path('payments/new', views.new_payment, name='new_payment'),
    path('close_contract', views.close_contract, name='close_contract'),
    #
    path('review', mobile_views.SummaryView.as_view(), name='review'),
    path('review/<str:room_id>', mobile_views.SummaryView.as_view(), name='review'),
    path('payment/<str:room_id>', mobile_views.RoomPaymentsView.as_view(), name='payment'),
    path('refresh_list/<str:room_id>', refresh_list_rooms, name='refresh_list_summary')
]

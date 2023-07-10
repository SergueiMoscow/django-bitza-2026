from django.urls import path, re_path

from rent import views
from rent.controllers.ContractView import ContractListView
from rent.controllers.PaymentView import PaymentListView

urlpatterns = [
    path('summary', views.summary, name='summary'),
    path('clients', views.clients, name='clients'),
    # path('payments', views.payments, name='payments'),
    # path('contracts', views.contracts, name='contracts'),
    path('payments', PaymentListView.as_view(), name='payments'),
    path('contracts', ContractListView.as_view(), name='contracts'),
    re_path(r'contacts/list', views.query_contacts, name='query_contacts'),
    path('payments/new', views.new_payment, name='new_payment'),
    path('close_contract', views.close_contract, name='close_contract'),
]
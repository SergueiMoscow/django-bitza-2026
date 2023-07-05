from django.urls import path, re_path

from rent import views
from rent.controllers.ContractView import ContractListView

urlpatterns = [
    path('summary', views.summary, name='summary'),
    path('payments', views.payments, name='payments'),
    path('clients', views.clients, name='clients'),
    # path('contracts', views.contracts, name='contracts'),
    path('contracts', ContractListView.as_view(), name='contracts'),
    re_path(r'contacts/list', views.query_contacts, name='query_contacts'),
    path('payments/new', views.new_payment, name='new_payment'),
]
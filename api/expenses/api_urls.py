from django.urls import path

from api.expenses.views import GetChequesView, GetChequeDetailsView

app_name = 'expenses'

urlpatterns = [
    path('cheques/', GetChequesView.as_view(), name='api_cheques'),
    path('chequedetails/', GetChequeDetailsView.as_view(), name='api_chequedetails'),
]

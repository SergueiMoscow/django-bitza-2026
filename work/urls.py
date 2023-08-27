from django.urls import path

from work.controllers.ListByUserView import ListByUserView

app_name = 'work'

urlpatterns = [
    path('list/', ListByUserView.as_view(), name='list'),
    path('', ListByUserView.as_view(), name='list'),
]

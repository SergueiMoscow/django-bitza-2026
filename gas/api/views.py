from rest_framework import generics

from gas.api.serializers import GasRecordSerializer
from gas.models import GasRecord


class GasRecordListCreateAPIView(generics.ListCreateAPIView):
    queryset = GasRecord.objects.all().order_by('-date')
    serializer_class = GasRecordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        room = self.request.query_params.get('room')
        if room:
            qs = qs.filter(room=room)
        return qs


class GasRecordDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = GasRecord.objects.all()
    serializer_class = GasRecordSerializer

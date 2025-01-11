# expenses/grpc_client.py

import grpc
from api.expenses.cheques_service import cheques_service_pb2_grpc, cheques_service_pb2
from bitza import settings
from google.protobuf import timestamp_pb2



class ChequeServiceClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(settings.BILLS_GRPC_SERVER_ADDRESS)
        self.stub = cheques_service_pb2_grpc.ChequeServiceStub(self.channel)

    def build_timestamp(self, dt):
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp

    def get_cheques(self, filter_data):
        filter_proto = cheques_service_pb2.ChequeFilter()
        token = settings.BILLS_SERVICE_TOKEN

        if filter_data.get('start_date'):
            filter_proto.start_date.CopyFrom(self.build_timestamp(filter_data['start_date']))
        if filter_data.get('end_date'):
            filter_proto.end_date.CopyFrom(self.build_timestamp(filter_data['end_date']))
        if filter_data.get('seller'):
            filter_proto.seller = filter_data['seller']
        if filter_data.get('notes'):
            filter_proto.notes = filter_data['notes']
        if filter_data.get('total_op'):
            filter_proto.total_op = filter_data['total_op']
        if filter_data.get('total_value') is not None:
            filter_proto.total_value = filter_data['total_value']
        if filter_data.get('search'):
            filter_proto.search = filter_data['search']

        request = cheques_service_pb2.GetChequesRequest(
            filter=filter_proto,
            token=token
        )

        response = self.stub.GetCheques(request)
        return response
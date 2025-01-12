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

    def get_cheque_details(self, filter_data):
        token = settings.BILLS_SERVICE_TOKEN

        details_proto = cheques_service_pb2.ChequeDetailsFilter()

        # Заполнение фильтра
        if filter_data.get('start_date'):
            details_proto.start_date.CopyFrom(self.build_timestamp(filter_data['start_date']))
        if filter_data.get('end_date'):
            details_proto.end_date.CopyFrom(self.build_timestamp(filter_data['end_date']))
        if filter_data.get('seller'):
            details_proto.seller = filter_data['seller']
        if filter_data.get('notes'):
            details_proto.notes = filter_data['notes']
        if filter_data.get('total_op'):
            details_proto.total_op = filter_data['total_op']
        if filter_data.get('total_value') is not None:
            details_proto.total_value = filter_data['total_value']
        if filter_data.get('item_name'):
            details_proto.item_name = filter_data['item_name']
        if filter_data.get('item_price_op'):
            details_proto.item_price_op = filter_data['item_price_op']
        if filter_data.get('item_price_value') is not None:
            details_proto.item_price_value = filter_data['item_price_value']
        if filter_data.get('item_total_op'):
            details_proto.item_total_op = filter_data['item_total_op']
        if filter_data.get('item_total_value') is not None:
            details_proto.item_total_value = filter_data['item_total_value']
        if filter_data.get('search'):
            details_proto.search = filter_data['search']

        request = cheques_service_pb2.GetChequeDetailsRequest(
            filter=details_proto,
            token=token
        )

        response = self.stub.GetChequeDetails(request)
        return response
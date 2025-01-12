from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ChequeFilterSerializer
from .serializers import ChequeDetailsFilterSerializer
from .grpc_client import ChequeServiceClient
import grpc

class GetChequesView(APIView):

    def get(self, request, *args, **kwargs):
        serializer = ChequeFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return Response({"detail": "Authorization token missing"}, status=status.HTTP_401_UNAUTHORIZED)

        grpc_client = ChequeServiceClient()

        try:
            grpc_response = grpc_client.get_cheques(validated_data)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                return Response({"detail": "Invalid filter parameters"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            grpc_client.channel.close()

        cheques = []
        for cheque in grpc_response.cheques:
            cheques.append({
                "id": cheque.id,
                "file_name": cheque.file_name,
                "purchase_date": cheque.purchase_date.ToDatetime().isoformat() if cheque.HasField(
                    'purchase_date') else None,
                "user": cheque.user,
                "seller": cheque.seller,
                "account": cheque.account,
                "total": cheque.total,
                "notes": cheque.notes,
                "created_at": cheque.created_at.ToDatetime().isoformat() if cheque.HasField('created_at') else None,
                "updated_at": cheque.updated_at.ToDatetime().isoformat() if cheque.HasField('updated_at') else None,
            })

        return Response({"cheques": cheques}, status=status.HTTP_200_OK)


class GetChequeDetailsView(APIView):

    def get(self, request, *args, **kwargs):
        serializer = ChequeDetailsFilterSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return Response({"detail": "Authorization token missing"}, status=status.HTTP_401_UNAUTHORIZED)

        grpc_client = ChequeServiceClient()

        try:
            grpc_response = grpc_client.get_cheque_details(validated_data)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                return Response({"detail": "Invalid filter parameters"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            grpc_client.channel.close()

        details = []
        for detail_with_head in grpc_response.detail_with_head:
            details.append({
                "head": {
                    "id": detail_with_head.head.id,
                    "store_location": detail_with_head.head.store_location,
                    "total_amount": detail_with_head.head.total_amount,
                    "seller": detail_with_head.head.seller,
                    "date": detail_with_head.head.date,
                },
                "detail": {
                    "id": detail_with_head.detail.id,
                    "name": detail_with_head.detail.name,
                    "price": detail_with_head.detail.price,
                    "quantity": detail_with_head.detail.quantity,
                    "total": detail_with_head.detail.total,
                    "category": detail_with_head.detail.category,
                    "created_at": detail_with_head.detail.created_at.ToDatetime().isoformat() if detail_with_head.detail.HasField('created_at') else None,
                    "updated_at": detail_with_head.detail.updated_at.ToDatetime().isoformat() if detail_with_head.detail.HasField('updated_at') else None,
                }
            })

        return Response({"details": details}, status=status.HTTP_200_OK)
import os

from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from weasyprint import HTML

from bitza.settings import BASE_DIR
from rent.models import Contract, ContractForm
from api.rent.serializers import GeneratePDFSerializer


TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates', 'contract_templates')

class GenerateContractPDFView(APIView):
    def post(self, request):
        serializer = GeneratePDFSerializer(data=request.data)
        if serializer.is_valid():
            contract_id = serializer.validated_data['contract_id']
            template_id = serializer.validated_data['template_id']

            try:
                contract = Contract.objects.select_related('contact', 'room').get(pk=contract_id)
                template = ContractForm.objects.get(pk=template_id)
            except Contract.DoesNotExist:
                return Response({"error": "Договор не найден"}, status=status.HTTP_404_NOT_FOUND)
            except ContractForm.DoesNotExist:
                return Response({"error": "Шаблон не найден"}, status=status.HTTP_404_NOT_FOUND)

            context = {
                'contract': contract,
                'contact': contract.contact,
                'room': contract.room,
            }

            html_string = render_to_string(os.path.join(TEMPLATES_DIR, template.html_file), context)
            html = HTML(string=html_string)
            pdf = html.write_pdf()

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="contract_{contract_id}.pdf"'
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

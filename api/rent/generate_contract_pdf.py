import os
from datetime import timedelta

from django.db.models import Max
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from weasyprint import HTML

from api.rent.rent_settings import CONTRACT_MAX_DURATION_DAYS
from bitza.settings import BASE_DIR
from rent.models import Contract, ContractForm, ContractPrint, get_latest_contract_form
from api.rent.serializers import GeneratePDFSerializer


TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates', 'contract_templates')

class GenerateContractPDFView(APIView):
    def post(self, request):
        serializer = GeneratePDFSerializer(data=request.data)
        if serializer.is_valid():
            contract_id = serializer.validated_data['contract_id']

            # Получаем контракт
            try:
                contract = Contract.objects.select_related('contact', 'room').get(pk=contract_id)
            except Contract.DoesNotExist:
                return Response({"error": "Договор не найден"}, status=status.HTTP_404_NOT_FOUND)

            # Пытаемся получить самый последний ContractPrint для контракта
            latest_print = ContractPrint.objects.filter(contract=contract).order_by('-date').first()

            if latest_print and latest_print.form:
                # Если есть запись ContractPrint с ненулевым form
                template = latest_print.form
                date_begin = latest_print.date
            elif contract.form:
                # Если нет подходящей записи в ContractPrint, используем contract.form
                template = contract.form
                date_begin = contract.date_begin
            else:
                # Если и там нет, используем последний доступный шаблон
                template = get_latest_contract_form()
                date_begin = contract.date_begin  # Или другое подходящее значение

            # Рассчитываем дату окончания
            date_end = date_begin + timedelta(days=CONTRACT_MAX_DURATION_DAYS)

            # Формируем контекст для шаблона
            context = {
                'contract': contract,
                'contact': contract.contact,
                'room': contract.room,
                'date_begin': date_begin,
                'date_end': date_end,
            }

            # Рендерим HTML из шаблона
            template_path = os.path.join(TEMPLATES_DIR, template.html_file)
            html_string = render_to_string(template_path, context)

            # Генерируем PDF из HTML
            html = HTML(string=html_string)
            pdf = html.write_pdf()

            # Формируем HTTP-ответ с PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="contract_{contract_id}.pdf"'
            return response

        # Если сериализация не удалась, возвращаем ошибки
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateContractPDFView_DELETE(APIView):
    # TODO: delete this class
    def post(self, request):
        serializer = GeneratePDFSerializer(data=request.data)
        if serializer.is_valid():
            contract_id = serializer.validated_data['contract_id']

            try:
                contract = Contract.objects.select_related('contact', 'room').get(pk=contract_id)
                template = ContractForm.objects.get(pk=contract.form)
            except Contract.DoesNotExist:
                return Response({"error": "Договор не найден"}, status=status.HTTP_404_NOT_FOUND)
            except ContractForm.DoesNotExist:
                return Response({"error": "Шаблон не найден"}, status=status.HTTP_404_NOT_FOUND)

            latest_print = ContractPrint.object.filter(contract=contract).aggregate(Max('date'))
            date_begin = latest_print['date__max'] if latest_print['date__max'] else contract.date_begin
            date_end = date_begin + timedelta(CONTRACT_MAX_DURATION_DAYS)
            template = ContractForm.objects.get(pk=latest_print.form) if latest_print.form else contract.form;
            context = {
                'contract': contract,
                'contact': contract.contact,
                'room': contract.room,
                'date_begin': date_begin,
                'date_end': date_end,
            }

            html_string = render_to_string(os.path.join(TEMPLATES_DIR, template.html_file), context)
            html = HTML(string=html_string)
            pdf = html.write_pdf()

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="contract_{contract_id}.pdf"'
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic.list import ListView

from bitza.common_functions import get_menu_items_by_group
from rent.models import Contact


class ContactListView(ListView):
    model = Contact
    template_name = 'rent/contacts.html'
    paginate_by = 30
    context_object_name = 'contacts'

    def get_template_names(self):
        if self.request.GET.get('container') == 'div':
            return ['rent/contacts_list.html', 'rent/contacts.html']
        else:
            return [self.template_name]

    def get_queryset(self):
        if self.request.GET.get('q'):
            return Contact.objects.all().filter(
                Q(surname__icontains=self.request.GET.get('q')) |
                Q(name__icontains=self.request.GET.get('q'))
            ).order_by('-created_at')
        else:
            return Contact.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = get_menu_items_by_group('owners')
        context['labels'] = ['Фамилия', 'Имя', 'Дата рожд.', 'Город']
        # context['form'] = ContactModelForm()
        queryset = self.get_queryset()  # Contact.objects.all().order_by('-created_at')
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        print("Всего элементов:", len(context['contacts']))
        print("Page_obj: ", context['page_obj'])
        return context

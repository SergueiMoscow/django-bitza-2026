from django import forms

from work.models import Work


class BeginWorkForm(forms.ModelForm):

    class Meta:
        model = Work
        fields = []


class EndWorkForm(forms.ModelForm):

    class Meta:
        model = Work
        fields = ['project', 'description']
        labels = [{
            'project': 'Проект',
            'description': 'Описание',
        }]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 50, 'placeholder': 'Описание', 'is_required': True})
        }

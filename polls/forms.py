from django import forms


class ShowImageForm(forms.Form):
    width = forms.CharField(label='Width', required=True, help_text='Provide width')
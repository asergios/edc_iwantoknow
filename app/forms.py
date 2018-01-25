from django import forms
from django.core.exceptions import ValidationError
from datetime import date

class DateForm(forms.Form):
    formats = ['%Y-%m-%d', '%d-%m-%Y']
    date = forms.DateField(input_formats= formats, label='', widget=forms.TextInput(attrs={'class': 'date-input'}), initial=date.today)

    # Days after today or today are not allowed
    def clean_date(self):
        typed = self.cleaned_data.get('date', '')

        if date.today() <= typed:
            raise ValidationError("I don't think you can be born tomorrow...")

        return self.cleaned_data.get('date', '')

class InputForm(forms.Form):
    input_form = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'char-input'}), initial="Moscow")
    


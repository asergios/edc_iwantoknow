from django import forms
import datetime

class DateForm(forms.Form):
    date = forms.DateField(label='', widget=forms.TextInput(attrs={'class': 'date-input'}), initial=datetime.date.today)
    


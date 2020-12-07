from django import forms


class QueryForm(forms.Form):
    query = forms.CharField(label='Your query', max_length=200)

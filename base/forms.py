# from django import forms
from .models import *
# class DayMenuForm(forms.Form):
#     OPTIONS = [(item.id, item.name) for item in FoodItem.objects.all()]
#     items = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=OPTIONS)
    
# DayMenuFormSet = forms.formset_factory(DayMenuForm, extra=7)


from django import forms

class DayMenuForm(forms.Form):
    OPTIONS = [(item.id, item.name) for item in FoodItem.objects.all()]
    items = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=OPTIONS)
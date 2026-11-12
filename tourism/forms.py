import calendar
from django import forms
from .models import Category

MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]


class PreferenceForm(forms.Form):
    budget = forms.IntegerField(min_value=500, label="Budget per person (Rs)")
    days = forms.IntegerField(min_value=1, max_value=15, label="Number of days")
    people = forms.IntegerField(min_value=1, max_value=50, initial=1, label="Number of travellers")
    travel_month = forms.TypedChoiceField(choices=MONTH_CHOICES, coerce=int, label="Travel month")
    interests = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Interests",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("budget", "days", "people"):
            self.fields[name].widget.attrs["class"] = "form-control"
        self.fields["travel_month"].widget.attrs["class"] = "form-select"
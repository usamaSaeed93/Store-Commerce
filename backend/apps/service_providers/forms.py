from apps.address.models import Location
from django import forms

from apps.service_providers.models import ServiceProvider


class ServiceProviderForm(forms.ModelForm):
    location = forms.ChoiceField(
        required=False, choices=Location.objects.values_list("id", "street_address")
    )

    class Meta:
        model = ServiceProvider
        fields = [
            "buisness_type",
            "facility_name",
            "area_code",
            "phone_number",
            "fax_number",
            "email",
            "website",
            "unit_numbers",
            "size",
            "working_hours",
        ]

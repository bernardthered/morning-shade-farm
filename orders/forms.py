from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django import forms
from django.conf import settings
from django.db.models import Sum
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from .models import Order, DailyLimit


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = (
            'quantity',
            'requester_name',
            'requester_email',
            'requester_phone_number',
            'pickup_date',
            'comments',)

    def __init__(self, *args, submit_button_name="Submit", **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['requester_name'].label = "Your full name"
        self.fields['requester_email'].label = "Your email address"
        self.fields['requester_phone_number'].label = "Your phone number"
        self.fields['quantity'].label = "Number of pounds of blueberries"
        self.fields['requester_phone_number'].widget = PhoneNumberInternationalFallbackWidget(
            region='us')
        self.fields['pickup_date'].widget = \
            DateTimePicker(options={"format": "MM/DD/YYYY"})

        if settings.DEBUG and False:
            self.fields['quantity'].initial = 1000
            self.fields['requester_name'].initial = "Charles Reid"
            self.fields['requester_email'].initial = "creid@example.com"
            self.fields['requester_phone_number'].initial = "5035555678"
            self.fields['pickup_date'].initial = "06/20/2017"

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = 'submit_survey'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(*self.fields.keys())
        self.helper.add_input(Submit('submit', submit_button_name))

    def clean(self):
        pickup_date = self.cleaned_data.get('pickup_date')
        quantity = self.cleaned_data.get('quantity')

        if self.instance:
            # use the difference as the quantity to check. Ie. if they are going from 20 to 100
            # lbs, make sure an additional 80 would not exceed the limit
            if self.instance.pickup_date == pickup_date:
                quantity = quantity - self.instance.quantity
                if quantity <= 0:
                    # They are not changing the date, and the quantity is either the same or a
                    # decrease, so let them do this (even if it's still over the limit for the day)
                    return super(OrderForm, self).clean()
        limit = DailyLimit.get_limit_for_date(pickup_date)
        if not limit:
            return super(OrderForm, self).clean()
        already_requested = \
            Order.objects.filter(pickup_date=pickup_date).aggregate(Sum('quantity'))[
                'quantity__sum'] or 0
        overage = (already_requested + quantity) - limit
        if overage > 0:
            raise forms.ValidationError(
                "This order would put the total requests for {} {} pounds over the limit".format(
                    pickup_date, overage,
                )
            )
        return super(OrderForm, self).clean()

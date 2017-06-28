import datetime

from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Layout, Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.urls import reverse
from dynamic_preferences.registries import global_preferences_registry
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

from .models import Order, DailyLimit


def after_yesterday(value):
    if value < datetime.date.today():
        raise ValidationError("The pickup date cannot be in the past.")


def is_during_the_season(value):
    this_year = datetime.datetime.today().year
    if value.year != this_year:
        raise ValidationError("Orders are only allowed for {}.".format(this_year))

    global_preferences = global_preferences_registry.manager()

    start_day = global_preferences['season_start_day']
    end_day = global_preferences['season_end_day']
    start_of_season = datetime.date(year=this_year, month=6, day=start_day)
    end_of_season = datetime.date(year=this_year, month=9, day=end_day)

    if value < start_of_season:
        raise ValidationError("The pick up season starts June {}.".format(start_day))

    if value > end_of_season:
        raise ValidationError("The pick up season ends Sept {}.".format(end_day))


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

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['requester_name'].label = "Your full name"
        self.fields['requester_email'].label = "Your email address"
        self.fields['requester_phone_number'].label = "Your phone number"
        self.fields['quantity'].label = "Number of pounds of blueberries"
        self.fields['requester_phone_number'].widget = PhoneNumberInternationalFallbackWidget(
            region='us')
        self.fields['pickup_date'].widget = \
            DateTimePicker(options={"format": "MM/DD/YYYY"})
        self.fields['pickup_date'].validators=[after_yesterday, is_during_the_season,]

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
        order = kwargs.get('instance', None)
        if order:
            if order.status == "CANCELED":
                for field_name in self.fields.keys():
                    self.fields[field_name].widget.attrs['readonly'] = True
            else:
                self.helper.add_input(Button(
                    'cancel', "Cancel Order", onclick="window.location.href='{}';".format(
                    reverse('cancel_order', kwargs={"order_id":order.id}))))
                self.helper.add_input(Submit('submit', "Update Order"))

        else:
            self.helper.add_input(Submit('submit', "Submit"))

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

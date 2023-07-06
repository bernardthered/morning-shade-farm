import datetime

from bootstrap3_datetime.widgets import DateTimePicker
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Layout, Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms import ChoiceField
from django.urls import reverse
from dynamic_preferences.registries import global_preferences_registry

from .models import Order, DailyLimit


def after_yesterday(value):
    if value < datetime.date.today():
        raise ValidationError("The pickup date cannot be in the past.")


def is_during_the_season(value=None, raise_exception=True):
    if not value:
        value = datetime.date.today()

    this_year = datetime.datetime.today().year
    if value.year != this_year:
        raise ValidationError(f"Orders are only allowed for {this_year}.")

    global_preferences = global_preferences_registry.manager()

    start_day = global_preferences["season_start_day"]
    start_month = global_preferences["season_start_month"]
    end_day = global_preferences["season_end_day"]
    end_month = global_preferences["season_end_month"]
    start_of_season = datetime.date(year=this_year, month=start_month, day=start_day)
    end_of_season = datetime.date(year=this_year, month=end_month, day=end_day)

    if value < start_of_season:
        if raise_exception:
            raise ValidationError(
                f"The pick up season starts {start_month}/{start_day}."
            )
        else:
            return False

    if value > end_of_season:
        if raise_exception:
            raise ValidationError(f"The pick up season ends {end_month}/{end_day}.")
        else:
            return False
    return True


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "quantity",
            "requester_name",
            "requester_email",
            "requester_phone_number",
            "pickup_date",
            "pickup_time",
            "comments",
        )

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields["requester_name"].label = "Your full name"
        self.fields["requester_email"].label = "Your email address"
        self.fields["requester_phone_number"].label = "Your phone number"
        self.fields["quantity"].label = "Number of pounds of blueberries"
        self.fields["pickup_date"].widget = DateTimePicker(
            options={"format": "MM/DD/YYYY"}
        )
        self.fields["pickup_date"].validators = [after_yesterday, is_during_the_season]
        time_choices = [(None, "Approximate pickup time"), *Order.TIME_CHOICES]
        self.fields["pickup_time"] = ChoiceField(choices=time_choices, required=True)

        if settings.DEBUG:
            self.fields["quantity"].initial = 1000
            self.fields["requester_name"].initial = "Bernard"
            self.fields["requester_email"].initial = "bernard@example.com"
            self.fields["requester_phone_number"].initial = "5035555678"
            self.fields["pickup_date"].initial = "12/10/2022"
            self.fields["pickup_time"].initial = 8

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_action = "submit_survey"
        self.helper.form_class = "form-inline"
        self.helper.field_template = "bootstrap3/layout/inline_field.html"
        self.helper.layout = Layout(*self.fields.keys())
        order = kwargs.get("instance", None)
        if order:
            if order.status == "CANCELED":
                for field_name in self.fields.keys():
                    self.fields[field_name].widget.attrs["readonly"] = True
            else:
                self.helper.add_input(
                    Button(
                        "cancel",
                        "Cancel Order",
                        onclick=f"window.location.href='{reverse('cancel_order', kwargs={'order_id': order.id})}';",
                    )
                )
                self.helper.add_input(Submit("submit", "Update Order"))

        else:
            self.helper.add_input(Submit("submit", "Submit"))

    def clean(self):
        pickup_date = self.cleaned_data.get("pickup_date")
        quantity = self.cleaned_data.get("quantity")
        if not quantity:
            # I received some errors that indicated quantity was somehow None here, not sure how
            # but let's fail early if it happens.
            raise ValidationError("Quantity cannot be none.", code="bad_quantity")

        if self.instance and self.instance.quantity:
            # use the difference as the quantity to check. Ie. if they are going from 20 to 100
            # lbs, make sure an additional 80 would not exceed the limit
            if self.instance.pickup_date == pickup_date:
                quantity = quantity - self.instance.quantity
                if quantity <= 0:
                    # They are not changing the date, and the quantity is either the same or a
                    # decrease, so let them do this (even if it's still over the limit for the day)
                    return super(OrderForm, self).clean()
        limit = DailyLimit.get_limit_for_date(pickup_date)
        if limit is None:
            # no limit, skip checking
            return super().clean()
        already_requested = (
            Order.objects.filter(pickup_date=pickup_date).aggregate(Sum("quantity"))[
                "quantity__sum"
            ]
            or 0
        )
        overage = (already_requested + quantity) - limit
        if overage > 0:
            raise forms.ValidationError(
                f"This order would put the total requests for {pickup_date} {overage} pounds over the limit"
            )
        return super(OrderForm, self).clean()

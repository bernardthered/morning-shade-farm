from crispy_forms.bootstrap import StrictButton, InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django import forms

from .models import Order


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('requester_name', 'requester_email', 'quantity', 'pickup_date', )

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['requester_name'].label = "Your full name"
        self.fields['requester_email'].label = "Your email address"
        self.fields['quantity'].label = "Number of pounds of blueberries"
        # self.fields['quantity'].initial = 1000
        # self.fields['pickup_date'].initial = "03/10/2017"

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = 'submit_survey'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'requester_name',
            'requester_email',
            'quantity',
            'pickup_date',
        )
        self.helper.add_input(Submit('submit', 'Submit'))

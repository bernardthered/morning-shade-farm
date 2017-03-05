from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from orders.forms import OrderForm


def index(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            msg = 'Your order for {} pounds of blueberries has been received. You can pick ' \
                  'them up on {}.'.format(
                order.quantity, order.pickup_date
            )
            messages.success(request, msg)
            return redirect('index')
        else:
            msg = mark_safe("The form has errors: {}".format("<BR>".join(form.errors)))
            msg = mark_safe("The form has errors: {}".format(form.errors))
            #messages.warning(request, msg)
            messages.add_message(request, messages.constants.ERROR, msg, extra_tags='danger')

    else:
        form = OrderForm()

    return render(request, 'orders/index.html', {'form': form})

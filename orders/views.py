from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from orders.forms import OrderForm
from orders.models import Price


def index(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            order.save()  # just to calculate & store the price

            msg = 'Your order for {} pounds of blueberries for ${} has been received. You can ' \
                  'pick them up after {} on {} at Morning Shade Farm.'.format(
                order.quantity, order.total_cost, order.pickup_date.time(),
                order.pickup_date.date(),
            )
            if order.quantity >= 200:
                msg += " If you have additional requests, please call the farm."

            messages.success(request, msg)
            return redirect('index')
        else:
            msg = mark_safe("The form has errors: {}".format(form.errors))
            messages.add_message(request, messages.constants.ERROR, msg, extra_tags='danger')
    else:
        form = OrderForm()

    prices = Price.objects.all().order_by('min_quantity')
    return render(request, 'orders/index.html', {'form': form, 'prices': prices})

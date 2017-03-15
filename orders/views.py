from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from orders.forms import OrderForm
from orders.models import Price, Order


def index(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            order.save()  # just to calculate & store the price

            msg = 'Your order for {} pounds of blueberries for ${} has been received. You can ' \
                  'pick them up after 9am on {} at Morning Shade Farm.'.format(
                order.quantity, order.total_cost, order.pickup_date,
            )
            if order.quantity >= 200:
                msg += " If you have additional requests, please add comments to your order or call us."

            messages.success(request, msg)
            return redirect('index')
        else:
            msg = mark_safe("The form has errors: {}".format(form.errors))
            messages.add_message(request, messages.constants.ERROR, msg, extra_tags='danger')
    else:
        form = OrderForm()

    prices = Price.objects.all().order_by('min_quantity')
    return render(request, 'orders/index.html', {'form': form, 'prices': prices})


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            order.save()  # just to calculate & store the price

            msg = 'Your order for {} pounds of blueberries for ${} has been received. You can ' \
                  'pick them up after 9am on {} at Morning Shade Farm.'.format(
                    order.quantity, order.total_cost, order.pickup_date,
                )
            if order.quantity >= 200:
                msg += " If you have additional requests, please call the farm."

            messages.success(request, msg)
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            msg = mark_safe("The form has errors: {}".format(form.errors))
            messages.add_message(request, messages.constants.ERROR, msg, extra_tags='danger')
    else:
        form = OrderForm(instance=order, submit_button_name="Update Order")

    return render(request, 'orders/order_detail.html', {
        'pagetitle': "Order {}".format(order.id),
        'form': form,
    })

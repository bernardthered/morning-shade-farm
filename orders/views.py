import datetime

import copy
from django.conf.urls import url
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from orders.forms import OrderForm
from orders.models import Price, Order, DailyLimit


def index(request):
    form = process_form(request, creating_new=True)
    if isinstance(form, HttpResponseRedirect):
        # the form is not a form, but a redirect. Return that now.
        return form
    prices = Price.objects.all().order_by('min_quantity')
    return render(request, 'orders/index.html', {'form': form, 'prices': prices})


def upcoming(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    day_totals = []
    cur_date = datetime.datetime.today()
    # for the next 100 days
    for i in range(100):
        day_total = {}
        the_days_orders = Order.objects.filter(pickup_date=cur_date)
        quant = the_days_orders.aggregate(Sum('quantity'))['quantity__sum']
        if not quant:
            quant = 0
        day_total['date'], _ = str(cur_date).split(maxsplit=1)
        daily_limit = DailyLimit.get_limit_for_date(cur_date)
        day_total['limit'] = "Limit: {} pounds".format(daily_limit)
        day_total['date_str'] = cur_date.strftime('%a %b %d')
        day_total['total_quantity'] = "{} pounds".format(quant)
        day_total['num_orders'] = the_days_orders.count()
        day_total['num_rejected_orders'] = the_days_orders.filter(status='REJECTED').count()
        day_totals.append(day_total)
        cur_date += datetime.timedelta(days=1)
    return render(request, 'orders/upcoming.html', {
        'day_totals': day_totals,
    })


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    form = process_form(request, order, submit_button_name="Update Order")
    if isinstance(form, HttpResponseRedirect):
        # the form is not a form, but a redirect. Return that now.
        return form

    return render(request, 'orders/order_detail.html', {
        'pagetitle': "Your {} Blueberry Order".format(order.status.capitalize(), order.id),
        'form': form,
    })


def process_form(request, order=None, submit_button_name="Submit", creating_new=False):
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order, submit_button_name=submit_button_name)
        if form.is_valid():
            order = form.save()
            order.save()  # just to calculate & store the price

            msg = 'Your order for {} pounds of blueberries for ${} has been received. You can ' \
                  'pick them up after 9am on {} at Morning Shade Farm.'.format(
                   order.quantity, order.total_cost, order.pickup_date.strftime("%a %b %d"),
            )
            if order.quantity >= 200:
                msg += " If you have additional requests, please add comments to your order or call us."

            if creating_new:
                msg += " You can <a href={}>see, update, and cancel your order here</a>.".format(
                    reverse('order_detail', args=[order.id]))

            messages.success(request, mark_safe(msg))
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            # The bootstrap inline form displays global errors automatically, so we will remove
            # them here. Other errors it does not display, so we need to add a message to the
            # page with those.
            non_global_errors = copy.copy(form.errors)
            if "__all__" in non_global_errors:
                del(non_global_errors["__all__"])
            if non_global_errors:
                msg = mark_safe("The form has errors: {}".format(non_global_errors))
                messages.add_message(request, messages.constants.ERROR, msg, extra_tags='danger')
    else:
        form = OrderForm(instance=order, submit_button_name=submit_button_name)
    return form

from django.contrib import messages
from django.shortcuts import render, redirect

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
        form = OrderForm()
    return render(request, 'orders/index.html', {'form': form})

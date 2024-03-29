import copy
import datetime
import logging

import sendgrid

from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

from orders.forms import is_during_the_season, OrderForm
from orders.models import Price, Order, DailyLimit

from sendgrid.helpers.mail import Email, Content, Mail

logger = logging.getLogger("testlogger")


def index(request):
    """
    If it's outside of June-Sept, show a page that tells them to come back during the season
    and links them to the main farm info site. Otherwise, show the main page with the order form.
    """
    if not is_during_the_season(raise_exception=False):
        return render(request, "orders/out_of_season.html", {})

    form = process_form(request, creating_new=True)
    if isinstance(form, HttpResponseRedirect):
        # the form is not a form, but a redirect. Return that now.
        return form
    prices = Price.objects.all().order_by("min_quantity")
    return render(request, "orders/index.html", {"form": form, "prices": prices})


def orders_for_day(request, date=None):
    if not date:
        date = datetime.date.today()
    print(date)
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    orders = Order.objects.filter(pickup_date=date).exclude(status="CANCELED")
    return render(
        request,
        "orders/orders_for_day.html",
        {
            "date": date,
            "orders": orders,
        },
    )


def upcoming(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    day_totals = []
    cur_date = datetime.datetime.today()
    # for the next 30 days
    for i in range(30):
        day_total = {}
        the_days_orders = Order.objects.filter(pickup_date=cur_date).exclude(
            status="CANCELED"
        )
        quant = the_days_orders.aggregate(Sum("quantity"))["quantity__sum"]
        if not quant:
            quant = 0
        day_total["date"], _ = str(cur_date).split(maxsplit=1)
        daily_limit = DailyLimit.get_limit_for_date(cur_date)
        day_total["limit"] = f"Limit: {daily_limit} pounds"
        day_total["date_str"] = cur_date.strftime("%a %b %d")
        day_total["total_quantity"] = f"{quant} pounds"
        day_total["num_orders"] = the_days_orders.count()
        day_total["num_rejected_orders"] = the_days_orders.filter(
            status="REJECTED"
        ).count()
        day_totals.append(day_total)
        cur_date += datetime.timedelta(days=1)
    return render(
        request,
        "orders/upcoming.html",
        {
            "day_totals": day_totals,
        },
    )


def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return render(request, "orders/order_not_found.html", {"order_id": order_id})

    form = process_form(request, order)
    if isinstance(form, HttpResponseRedirect):
        # the form is not a form, but a redirect. Return that now.
        return form

    return render(
        request,
        "orders/order_detail.html",
        {
            "pagetitle": f"Your {order.status.capitalize()} Blueberry Order {order.id}",
            "form": form,
        },
    )


def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "CANCELED"
    order.save()
    messages.info(request, "Your order has been canceled.")
    email_canceled_order_notification(request, order)
    return HttpResponseRedirect(reverse("index"))


def email_new_order_info(request, order):
    order_url = request.build_absolute_uri(location=reverse("order_detail", args=[order.id]))
    subject = f"{order.quantity} lbs of berries will be ready on {order.pretty_date}"
    body = f"""
    <p>We'll see you for your berry pickup on <strong>{order.pretty_date} from {order.pretty_time}</strong>!</p>
    
    <p>You can see, update, and cancel your order here: {order_url}</p>
    
    <p>
    Quantity: <strong>{order.quantity} pounds</strong><br>
    Cost: <strong>${order.total_cost}</strong><br>
    Order ID: {order.id}<br>
    </p>
    
    <p>
    Thanks for your order!
    Morning Shade Farm
    </p>
    """
    send_email(request, order.requester_email, subject, body)


def email_canceled_order_notification(request, order):
    subject = f"Your order for {order.quantity} lbs of berries has been canceled!"
    main_url = request.build_absolute_uri(location=reverse("index"))
    body = f"If you would like to place another order, you can do so here: {main_url}"
    send_email(request, order.requester_email, subject, body)


def send_email(request, recipient, subject, body):
    message = Mail(
        from_email=settings.EMAIL_FROM_ADDRESS,
        to_emails=recipient,
        subject=subject,
        html_content=body,
    )
    try:
        sendgrid_client = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        sendgrid_client.send(message)
        messages.info(
            request, "You will receive an email confirmation within about 10 minutes."
        )
    except Exception as err:
        messages.error(request, f"Unable to send email: {err}")
        logger.exception("Unable to send email")


def process_form(request, order=None, creating_new=False):
    """
    Called for generating the form initially, and processing it when submitted. Used by both the
    main index page (for new orders), and the order details page (for changing an order).
    """
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            order.save()  # just to calculate & store the price

            share_button = """<p>
                <div class="fb-share-button" data-href="http://www.morningshade.farm/" 
                data-layout="button" data-size="large">
                <a target="_blank" href="https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2Fwww.morningshade.farm%2F&amp;src=sdkpreparse" class="fb-xfbml-parse-ignore">Share</a>
                </div>
            """
            msg = (
                f"Your order for {order.quantity} pounds of blueberries for ${order.total_cost} has been received. You "
                f"can pick them up from {order.pretty_time} on {order.pretty_date} at Morning Shade Farm."
            )
            if order.quantity >= 200:
                msg += " If you have additional requests, please add comments to your order or call us."

            if creating_new:
                order_url = reverse("order_detail", args=[order.id])
                msg += f" You can <a href={order_url}>see, update, and cancel your order here</a>."

            msg += share_button

            messages.success(request, mark_safe(msg))

            if creating_new:
                email_new_order_info(request, order)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        else:
            # The bootstrap inline form displays global errors automatically, so we will remove
            # them here. Other errors it does not display, so we need to add a message to the
            # page with those.
            non_global_errors = copy.copy(form.errors)
            if "__all__" in non_global_errors:
                del non_global_errors["__all__"]
            if non_global_errors:
                msg = mark_safe(f"The form has errors: {non_global_errors}")
                messages.add_message(
                    request, messages.constants.ERROR, msg, extra_tags="danger"
                )
    else:
        form = OrderForm(instance=order)
    return form

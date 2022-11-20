from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(r"^orders/upcoming$", views.upcoming, name="upcoming"),
    re_path(r"^orders/for/$", views.orders_for_day, name="orders_for_day"),
    re_path(
        r"^orders/for/(?P<date>[0-9\-]+)/$", views.orders_for_day, name="orders_for_day"
    ),
    re_path(
        r"^orders/(?P<order_id>[0-9a-f\-]+)/$", views.order_detail, name="order_detail"
    ),
    re_path(
        r"^orders/(?P<order_id>[0-9a-f\-]+)/cancel/$",
        views.cancel_order,
        name="cancel_order",
    ),
]

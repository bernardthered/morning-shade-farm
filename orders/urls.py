from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^orders/upcoming$', views.upcoming, name='upcoming'),
    url(r'^orders/for/$', views.orders_for_day, name='orders_for_day'),
    url(r'^orders/for/(?P<date>[0-9\-]+)/$', views.orders_for_day, name='orders_for_day'),
    url(r'^orders/(?P<order_id>[0-9a-f\-]+)/$', views.order_detail, name='order_detail'),
    url(r'^orders/(?P<order_id>[0-9a-f\-]+)/cancel/$', views.cancel_order, name='cancel_order'),
]

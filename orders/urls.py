from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^orders/(?P<order_id>[0-9a-f\-]+)/$', views.order_detail, name='order_detail'),
]

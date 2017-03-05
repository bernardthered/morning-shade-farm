from django.contrib import admin
from rangefilter.filter import DateRangeFilter
from totalsum.admin import TotalsumAdmin

from .models import Order


def fulfill_order(modeladmin, request, queryset):
    queryset.update(status='FULFILLED')
fulfill_order.short_description = "Mark selected orders as fulfilled"


def cancel_order(modeladmin, request, queryset):
    queryset.update(status='CANCELED')
cancel_order.short_description = "Mark selected orders as canceled"


class OrderAdmin(TotalsumAdmin):
    totalsum_list = ('quantity',)
    unit_of_measure = 'lbs'

    exclude = []
    search_fields = ['requester_name', 'requester_email', 'quantity']
    list_filter = ['status', ('pickup_date', DateRangeFilter)]
    ordering = ['pickup_date', '-quantity']
    actions = [fulfill_order, cancel_order]
    list_display = (
        'status', 'pickup_date', 'quantity', 'requester_name', 'requester_email',
        'requester_phone_number', 'comments'
    )

admin.site.register(Order, OrderAdmin)

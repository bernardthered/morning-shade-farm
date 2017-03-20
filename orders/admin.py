from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin
from rangefilter.filter import DateRangeFilter
from totalsum.admin import TotalsumAdmin

from .models import Order, Price, DailyLimit


def fulfill_order(modeladmin, request, queryset):
    queryset.update(status='FILLED')
fulfill_order.short_description = "Mark selected orders as filled"


def cancel_order(modeladmin, request, queryset):
    queryset.update(status='CANCELED')
cancel_order.short_description = "Mark selected orders as canceled"


class OrderAdmin(TotalsumAdmin, ImportExportActionModelAdmin):
    totalsum_list = ('quantity', 'total_cost')

    exclude = []
    search_fields = ['requester_name', 'requester_email', 'quantity']
    list_filter = ['status', ('pickup_date', DateRangeFilter)]
    ordering = ['pickup_date', '-quantity']
    actions = [fulfill_order, cancel_order]
    list_display = (
        'status', 'pickup_date', 'quantity', 'requester_name',
        'requester_phone_number', 'comments',
    )
    readonly_fields = ['id', 'total_cost',]

admin.site.register(Order, OrderAdmin)
admin.site.register(Price)
admin.site.register(DailyLimit)

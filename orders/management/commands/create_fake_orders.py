import datetime

from django.core.management.base import BaseCommand
import random

from orders.models import Order


class Command(BaseCommand):
    help = """
    Usage:
        ./manage.py
    """

    def handle(self, *args, **options):
        cur_date = datetime.datetime.today()
        # for the next 100 days
        for i in range(100):
            # create 0-6 orders for this day
            for j in range(random.randint(0,6)):
                self.create_order(cur_date)
            cur_date += datetime.timedelta(days=1)


    def create_order(self, date):
        Order.objects.create(
            pickup_date=date, quantity=random.randint(1,20) * 10,
            requester_email="creid@example.com", requester_name="Charles Reid",
            requester_phone_number="5555551234")
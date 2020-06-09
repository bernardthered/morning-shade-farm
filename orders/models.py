import datetime
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


def multiple_of_ten(value):
    if value % 10 != 0:
        raise ValidationError(
            'The berries are sold in 10 pound bags, please enter a multiple of 10.')


def greater_than_zero(value):
    if value <= 0:
        raise ValidationError('{} is not greater than 0.'.format(value))


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('FILLED', 'Filled'),
        ('CANCELED', 'Canceled'),
    )
    TIME_CHOICES = (
        (8, "8-9am"),
        (9, "9-10am"),
        (10, "10-11am"),
        (11, "11am-noon"),
        (12, "noon-1pm"),
        (13, "1-2pm"),
        (14, "2-3pm"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    create_date = models.DateTimeField(default=datetime.datetime.now)
    last_updated = models.DateTimeField(default=datetime.datetime.now)
    pickup_date = models.DateField()
    pickup_time = models.IntegerField(choices=TIME_CHOICES, blank=True, null=True)
    quantity = models.IntegerField(validators=[multiple_of_ten, greater_than_zero])
    requester_name = models.CharField(max_length=128)
    requester_email = models.CharField(max_length=128, validators=[validate_email])
    requester_phone_number = PhoneNumberField(blank=True)
    comments = models.TextField(blank=True)
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=128, default="PENDING")
    total_cost = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.get_cost_per_pound()
        self.last_updated = datetime.datetime.now()
        return super(Order, self).save(*args, **kwargs)

    def get_cost_per_pound(self):
        """
        :return: a Decimal of the cost per pound of berries that this order qualifies for,
        based on its quantity.
        """
        # Get the first (lowest) price object which this # of pounds qualifies for. The first
        # object will be the highest minimum (and presumably the lowest price) because the Price
        # objects are ordered descending by min quantity
        price = Price.objects.filter(min_quantity__lte=self.quantity).first()
        return price.cost_per_pound

    @property
    def pretty_date(self):
        return self.pickup_date.strftime("%a %b %d")

    @property
    def pretty_time(self):
        return self.get_pickup_time_display()

    def __str__(self):
        return "{} order for {} pounds on {} for {}".format(
            self.status.capitalize(), self.quantity, self.pickup_date, self.requester_name)
    description = property(__str__)


class Price(models.Model):
    # eventually can add a FK to which product this is for
    cost_per_pound = models.DecimalField(max_digits=8, decimal_places=2)
    min_quantity = models.IntegerField()

    class Meta:
        ordering = ["-min_quantity"]

    def __str__(self):
        return "{} per lb. for orders over {} lbs.".format(self.cost_per_pound, self.min_quantity)


class DailyLimit(models.Model):
    limit = models.IntegerField()
    # When date is null, it is the global default limit
    # TODO: also enforce uniqueness of the null date
    date = models.DateField(null=True, blank=True, unique=True,
                            help_text="If left blank, this will be the default limit for all days.")

    @staticmethod
    def get_limit_for_date(date):
        limit_for_date = DailyLimit.objects.filter(date=date).first()
        if limit_for_date:
            return limit_for_date.limit
        global_limit = DailyLimit.objects.filter(date=None).first()
        if global_limit:
            return global_limit.limit
        return None

    def __str__(self):
        if not self.date:
            return "Default daily limit: {} pounds".format(self.limit)
        return "{} pound limit on {}".format(self.limit, self.date)


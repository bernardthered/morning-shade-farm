import datetime
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


def multiple_of_ten(value):
    if value % 10 != 0:
        raise ValidationError(
            'The berries are sold in 10 pound bags, please enter a multiple of 10.')


def greater_than_zero(value):
    if value <= 0:
        raise ValidationError('{} is not greater than 0.'.format(value))


def after_yesterday(value):
    if value < datetime.date.today():
        raise ValidationError("The pickup date cannot be in the past.")


def is_during_the_season(value):
    this_year = datetime.datetime.today().year
    if value.year != this_year:
        raise ValidationError("Orders are only allowed for {}.".format(this_year))

    start_of_season = datetime.date(year=this_year, month=6, day=17)
    end_of_season = datetime.date(year=this_year, month=9, day=15)

    if value < start_of_season:
        raise ValidationError("The pick up season starts June 17th.")

    if value > end_of_season:
        raise ValidationError("The pick up season ends Sept 15th.")


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('FILLED', 'Filled'),
        ('CANCELED', 'Canceled'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    create_date = models.DateTimeField(default=datetime.datetime.now)
    last_updated = models.DateTimeField(default=datetime.datetime.now)
    pickup_date = models.DateField(validators=[after_yesterday, is_during_the_season,])
    quantity = models.IntegerField(validators=[multiple_of_ten, greater_than_zero])
    requester_name = models.CharField(max_length=128)
    requester_email = models.CharField(max_length=128)
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

    def __str__(self):
        return "{} order for {} pounds on {} for {}".format(
            self.status.capitalize(), self.quantity, self.pickup_date, self.requester_name)
    description = property(__str__)


class Price(models.Model):
    """
    """
    # eventually can add a FK to which product this is for
    cost_per_pound = models.DecimalField(max_digits=8, decimal_places=2)
    min_quantity = models.IntegerField()

    class Meta:
        ordering = ["-min_quantity"]

    def __str__(self):
        return "{} per lb. for orders over {} lbs.".format(self.cost_per_pound, self.min_quantity)

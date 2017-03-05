from django.core.exceptions import ValidationError
from django.db import models


def multiple_of_ten(value):
    if value % 10 != 0:
        raise ValidationError('{} is not a multiple of 10.'.format(value))


def greater_than_zero(value):
    if value <= 0:
        raise ValidationError('{} is not greater than 0.'.format(value))


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELED', 'Canceled'),
    )
    pickup_date = models.DateField()
    quantity = models.IntegerField(validators=[multiple_of_ten, greater_than_zero])
    requester_name = models.CharField(max_length=128)
    requester_email = models.CharField(max_length=128)
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=128, default="PENDING")

    def __str__(self):
        return "{} order for {} pounds on {} for {}".format(
            self.status.capitalize(), self.quantity, self.pickup_date, self.requester_name)
    description = property(__str__)

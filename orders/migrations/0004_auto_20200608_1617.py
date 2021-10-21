# Generated by Django 2.2.13 on 2020-06-08 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_pickup_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='pickup_time',
            field=models.IntegerField(blank=True, choices=[(8, '8-9am'), (9, '9-10am'), (10, '10-11am'), (11, '11am-noon'), (12, 'noon-1pm'), (13, '1-2pm'), (14, '2-3pm')], null=True),
        ),
    ]
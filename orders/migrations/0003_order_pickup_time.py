# Generated by Django 2.2.13 on 2020-06-08 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20170628_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pickup_time',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
# Generated by Django 4.2 on 2023-05-09 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0009_remove_vehicle_is_available_vehicle_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentalrequest',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]

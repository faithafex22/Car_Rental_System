# Generated by Django 4.2 on 2023-05-09 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0011_rentalrequest_is_returned'),
    ]

    operations = [
        migrations.DeleteModel(
            name='VehicleAssignment',
        ),
    ]

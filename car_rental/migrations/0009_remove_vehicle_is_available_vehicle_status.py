# Generated by Django 4.2 on 2023-05-08 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0008_rentalrequest_reason_vehicleassignment_assigned_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='is_available',
        ),
        migrations.AddField(
            model_name='vehicle',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('rented', 'Rented'), ('in_maintenance', 'In_Maintenance')], default='available', max_length=20),
        ),
    ]

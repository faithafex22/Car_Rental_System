# Generated by Django 4.2 on 2023-05-08 08:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0007_remove_userprofile_profile_picture_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentalrequest',
            name='reason',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='vehicleassignment',
            name='assigned_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]

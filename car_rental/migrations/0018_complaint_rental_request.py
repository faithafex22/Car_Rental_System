# Generated by Django 4.2.1 on 2023-05-23 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0017_complaint_reply_rentalrequest_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='rental_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='car_rental.rentalrequest'),
        ),
    ]

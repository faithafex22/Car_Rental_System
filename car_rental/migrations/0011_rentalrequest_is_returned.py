# Generated by Django 4.2 on 2023-05-09 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0010_rentalrequest_is_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentalrequest',
            name='is_returned',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 4.2 on 2023-05-06 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0004_vehicle_is_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]

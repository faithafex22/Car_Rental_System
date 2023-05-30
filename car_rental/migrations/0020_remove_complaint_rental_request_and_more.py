# Generated by Django 4.2.1 on 2023-05-25 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0019_alter_complaint_rental_request'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complaint',
            name='rental_request',
        ),
        migrations.AlterField(
            model_name='complaint',
            name='vehicle',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='car_rental.vehicle'),
        ),
    ]

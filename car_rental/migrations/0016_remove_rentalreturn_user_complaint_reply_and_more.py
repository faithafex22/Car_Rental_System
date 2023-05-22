# Generated by Django 4.2.1 on 2023-05-19 13:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0015_alter_rating_vehicle'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rentalreturn',
            name='user',
        ),
        
        
        migrations.AddField(
            model_name='rentalreturn',
            name='rental_request',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='car_rental.rentalrequest'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='full_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
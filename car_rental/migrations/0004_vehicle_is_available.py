# Generated by Django 4.2 on 2023-05-06 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0003_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]
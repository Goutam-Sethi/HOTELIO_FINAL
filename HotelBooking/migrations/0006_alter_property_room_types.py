# Generated by Django 5.2 on 2025-04-30 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HotelBooking', '0005_alter_property_room_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='room_types',
            field=models.JSONField(default=dict),
        ),
    ]

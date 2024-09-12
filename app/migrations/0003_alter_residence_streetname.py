# Generated by Django 5.1.1 on 2024-09-10 13:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_location_unique_location_combination'),
    ]

    operations = [
        migrations.AlterField(
            model_name='residence',
            name='streetName',
            field=models.CharField(max_length=9, validators=[django.core.validators.RegexValidator(message='Write a valid Street Name \n i.e: KK 000 St or KG 000 St or KN 000 St', regex='^K[KNG] \\d{3} St$')]),
        ),
    ]
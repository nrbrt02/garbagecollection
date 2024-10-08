# Generated by Django 5.1.1 on 2024-09-10 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_residence_streetname'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='residence',
            options={'ordering': ['created_at']},
        ),
        migrations.AddConstraint(
            model_name='residence',
            constraint=models.UniqueConstraint(fields=('location', 'streetName', 'gateNumber'), name='unique_residence_combination'),
        ),
    ]

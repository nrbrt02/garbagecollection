# Generated by Django 5.1.1 on 2024-09-13 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_schedule_plate'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='day',
            field=models.CharField(choices=[('MONDAY', 'Monday'), ('TUESDAY', 'Tuesday'), ('WEDNESDAY', 'Wednesday'), ('THURSDAY', 'Thursday'), ('FRIDAY', 'Friday'), ('SATURDAY', 'Saturday'), ('SUNDAY', 'Sunday')], default='MONDAY', max_length=20),
            preserve_default=False,
        ),
    ]

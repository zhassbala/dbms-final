# Generated by Django 4.1.4 on 2022-12-13 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_registration_patient_alter_registration_calendar'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='rank',
            field=models.IntegerField(default=0),
        ),
    ]

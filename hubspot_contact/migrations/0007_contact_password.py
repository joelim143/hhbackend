# Generated by Django 5.1.6 on 2025-02-08 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hubspot_contact', '0006_contact_availability_contact_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='password',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]

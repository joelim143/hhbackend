# Generated by Django 5.1.6 on 2025-02-12 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hubspot_contact', '0008_contact_approval_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

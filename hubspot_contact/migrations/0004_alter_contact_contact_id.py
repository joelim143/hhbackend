# Generated by Django 5.1.4 on 2025-01-16 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hubspot_contact", "0003_alter_contact_contact_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="contact_id",
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]

# Generated by Django 4.2.13 on 2024-05-20 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_order_premium_remove_order_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ordered',
            field=models.BooleanField(default=False),
        ),
    ]

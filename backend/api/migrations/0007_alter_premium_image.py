# Generated by Django 4.2.13 on 2024-05-25 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_premium_is_active_remove_profile_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='premium',
            name='image',
            field=models.ImageField(blank=True, upload_to='uploads/premium/'),
        ),
    ]

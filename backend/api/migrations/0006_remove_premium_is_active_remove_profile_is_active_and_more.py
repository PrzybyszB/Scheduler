# Generated by Django 4.2.13 on 2024-05-25 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_order_ordered'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='premium',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='publictransporttype',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='stop',
            name='is_active',
        ),
        migrations.AddField(
            model_name='premium',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='publictransporttype',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='stop',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
    ]

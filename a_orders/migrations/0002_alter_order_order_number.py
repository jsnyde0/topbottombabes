# Generated by Django 5.0.7 on 2024-07-22 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(editable=False, max_length=6, unique=True),
        ),
    ]

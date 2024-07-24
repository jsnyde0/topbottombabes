# Generated by Django 5.0.7 on 2024-07-22 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a_orders', '0005_alter_orderitem_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('CREDIT_CARD', 'Credit Card'), ('PAYPAL', 'PayPal'), ('BANK_TRANSFER', 'Bank Transfer')], max_length=20, null=True),
        ),
    ]
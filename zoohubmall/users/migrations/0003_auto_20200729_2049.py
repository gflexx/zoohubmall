# Generated by Django 2.2.9 on 2020-07-29 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200723_2356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='is_buyer',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='is_seller',
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_type',
            field=models.CharField(choices=[('is_buyer', 'I just want to buy stuff'), ('is_seller', 'Buy and sell my products here')], default='is_buyer', max_length=9),
        ),
    ]
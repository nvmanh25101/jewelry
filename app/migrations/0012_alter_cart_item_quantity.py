# Generated by Django 3.2 on 2023-08-14 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20230814_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart_item',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]

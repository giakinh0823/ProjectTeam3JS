# Generated by Django 2.2.5 on 2021-01-01 07:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appProduct', '0027_size_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='color',
            name='product',
        ),
        migrations.RemoveField(
            model_name='size',
            name='product',
        ),
    ]
# Generated by Django 5.0.12 on 2025-02-25 15:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_remove_ediciones_precio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ediciones',
            name='Foto',
        ),
    ]

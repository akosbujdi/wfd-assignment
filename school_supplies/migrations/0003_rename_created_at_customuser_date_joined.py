# Generated by Django 5.1.6 on 2025-04-22 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school_supplies', '0002_rename_inv_manage_item_inv_manage_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='created_at',
            new_name='date_joined',
        ),
    ]

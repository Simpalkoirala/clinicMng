# Generated by Django 5.2.1 on 2025-05-16 14:50

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_activitylog_viewed_alter_activitylog_profile'),
        ('patient', '0018_labreport_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='profile',
            field=models.ForeignKey(help_text=' Patient Profile', on_delete=django.db.models.deletion.CASCADE, related_name='patients_appointments', to='account.profile'),
        ),
        migrations.AlterField(
            model_name='labreport',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]

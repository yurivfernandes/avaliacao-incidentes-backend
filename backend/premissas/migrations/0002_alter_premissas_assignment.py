# Generated by Django 4.2.10 on 2025-01-28 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dw_analytics', '0008_rename_assignment_group_id_incident_assignment_group_and_more'),
        ('premissas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='premissas',
            name='assignment',
            field=models.ForeignKey(help_text='Assignment Group relacionado', on_delete=django.db.models.deletion.PROTECT, related_name='premissas', to='dw_analytics.assignmentgroup', unique=True),
        ),
    ]

# Generated by Django 3.2 on 2025-03-21 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_chatroom_document_enterprise_message_notification_report_team_teamuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='enterprise',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.enterprise'),
        ),
    ]

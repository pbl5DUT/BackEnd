# Generated by Django 4.2 on 2025-04-19 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_chatroom_id_message_chatroom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('Planned', 'Planned'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed'), ('On Hold', 'On Hold')], default='Ongoing', max_length=20),
        ),
    ]

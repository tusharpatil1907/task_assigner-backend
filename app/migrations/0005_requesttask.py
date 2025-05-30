# Generated by Django 5.1.7 on 2025-03-25 20:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_status_remove_task_completed_alter_user_tasks_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestTask',
            fields=[
                ('request_ID', models.AutoField(primary_key=True, serialize=False)),
                ('tasks', models.ManyToManyField(related_name='request_tasks', to='app.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

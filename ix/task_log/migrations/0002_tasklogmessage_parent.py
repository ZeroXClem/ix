# Generated by Django 4.2 on 2023-04-20 01:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("task_log", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="tasklogmessage",
            name="parent",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="task_log.tasklogmessage",
            ),
        ),
    ]

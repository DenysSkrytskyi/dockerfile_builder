# Generated by Django 4.2.7 on 2023-11-24 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rest_api", "0003_rename_username_dockerfilebuild_docker_username_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dockerfilebuild",
            name="docker_repo",
            field=models.CharField(default=None, max_length=128),
        ),
    ]
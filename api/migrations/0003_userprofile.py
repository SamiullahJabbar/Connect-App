# Generated by Django 5.1.6 on 2025-02-25 15:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_user_phone_number_user_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skills', models.TextField(blank=True, null=True)),
                ('experience', models.PositiveIntegerField(default=0)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('education', models.CharField(blank=True, max_length=255, null=True)),
                ('about_me', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

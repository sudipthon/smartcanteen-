# Generated by Django 5.0.6 on 2024-05-20 19:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_course_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='breaktime',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_breaktimes', to='base.course'),
        ),
        migrations.AlterField(
            model_name='orders',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]

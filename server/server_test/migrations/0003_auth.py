# Generated by Django 5.0 on 2024-03-10 00:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_test', '0002_event_teacher_course_experience_expertise_openclass_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='auth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=30)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_test.teacher')),
            ],
        ),
    ]

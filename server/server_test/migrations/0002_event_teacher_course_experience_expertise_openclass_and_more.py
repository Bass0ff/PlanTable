# Generated by Django 5.0 on 2024-03-07 03:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_test', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('subject', models.CharField(max_length=30)),
                ('qualification', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.TextField()),
                ('form', models.CharField(max_length=20)),
                ('document', models.CharField(max_length=20)),
                ('place', models.CharField(max_length=50)),
                ('organizer', models.CharField(max_length=50)),
                ('length', models.IntegerField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_test.event')),
            ],
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.TextField()),
                ('result', models.CharField(max_length=15)),
                ('form', models.CharField(max_length=20)),
                ('document', models.CharField(max_length=20)),
                ('place', models.CharField(max_length=50)),
                ('action', models.CharField(max_length=30)),
                ('level', models.CharField(max_length=20)),
                ('link', models.URLField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_test.event')),
            ],
        ),
        migrations.CreateModel(
            name='Expertise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(max_length=15)),
                ('action', models.CharField(max_length=30)),
                ('level', models.CharField(max_length=20)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_test.event')),
            ],
        ),
        migrations.CreateModel(
            name='OpenClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('studClass', models.CharField(max_length=3)),
                ('theme', models.TextField()),
                ('target', models.TextField()),
                ('result', models.CharField(max_length=15)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_test.event')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form', models.CharField(max_length=20)),
                ('document', models.CharField(max_length=20)),
                ('place', models.CharField(max_length=50)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_test.event')),
            ],
        ),
        migrations.CreateModel(
            name='StudentWork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(max_length=30)),
                ('theme', models.CharField(max_length=30)),
                ('student', models.CharField(max_length=50)),
                ('studClass', models.CharField(max_length=3)),
                ('level', models.CharField(max_length=20)),
                ('document', models.CharField(max_length=20)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_test.event')),
            ],
        ),
        migrations.CreateModel(
            name='SelfEd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin', models.DateField()),
                ('end', models.DateField()),
                ('theme', models.TextField()),
                ('method', models.TextField()),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_test.teacher')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server_test.teacher'),
        ),
    ]

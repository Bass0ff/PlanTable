# Generated by Django 5.0 on 2024-04-09 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_test', '0009_remove_course_id_remove_experience_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='department',
            field=models.CharField(default='none', max_length=45),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='teacher',
            name='access',
            field=models.CharField(max_length=15),
        ),
    ]

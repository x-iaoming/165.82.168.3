# Generated by Django 2.2.2 on 2019-06-28 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0010_auto_20190627_1914'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='username',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
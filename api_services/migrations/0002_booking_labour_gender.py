# Generated by Django 4.1 on 2023-07-29 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='labour_gender',
            field=models.CharField(default='Male', max_length=10),
        ),
    ]
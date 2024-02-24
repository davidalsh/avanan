# Generated by Django 4.2.10 on 2024-02-23 21:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dlp', '0001_initial'),
        ('slack', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='flaggedmessage',
            name='pattern',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dlp.dlppattern'),
        ),
    ]
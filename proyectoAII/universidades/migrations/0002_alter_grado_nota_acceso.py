# Generated by Django 3.2 on 2021-05-07 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('universidades', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grado',
            name='nota_acceso',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
# Generated by Django 4.2.7 on 2024-01-28 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='address',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Адрес работы'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='contact_email',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Контактный e-mail'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='contact_name',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Контактное имя'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Контактный телефон'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='language',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Знание языков'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='place',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Место работы'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='requirements',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Условия и требования'),
        ),
        migrations.AlterField(
            model_name='vacancy',
            name='salary',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Зарплата'),
        ),
    ]

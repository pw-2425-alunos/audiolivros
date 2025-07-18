# Generated by Django 4.0.6 on 2025-05-16 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tfc', '0009_like'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.FloatField(help_text='Posição em segundos')),
                ('atualizado', models.DateTimeField(auto_now=True)),
                ('audiolivro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tfc.audiolivro')),
                ('familia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tfc.familia')),
            ],
            options={
                'ordering': ['-atualizado'],
                'unique_together': {('familia', 'audiolivro')},
            },
        ),
    ]

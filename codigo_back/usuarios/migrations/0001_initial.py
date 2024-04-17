# Generated by Django 4.2 on 2024-04-16 04:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hospitales', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('tipo_sangre', models.CharField(blank=True, max_length=10, null=True)),
                ('telefono', models.BigIntegerField(blank=True, null=True)),
                ('tipo_identificacion', models.CharField(blank=True, max_length=5, null=True)),
                ('identificacion', models.IntegerField(blank=True, null=True)),
                ('tipo_usuario', models.CharField(blank=True, max_length=15, null=True)),
                ('eps', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospitales.eps')),
                ('hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hospitales.hospital')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perfil_usuario', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='usuario',
            constraint=models.UniqueConstraint(fields=('tipo_identificacion', 'identificacion'), name='unique_identification'),
        ),
    ]

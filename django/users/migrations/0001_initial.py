# Generated by Django 3.0.4 on 2020-04-14 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('preset_target', models.IntegerField(default=20)),
                ('today_progress', models.IntegerField(default=0)),
                ('revise_strategy', models.TextField(choices=[('forgetting curve', 'forgetting curve'), ('by last test date', 'by last test date')], default='forgetting curve')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

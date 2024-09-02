# Generated by Django 5.0.4 on 2024-09-01 15:31

import django.db.models.deletion
import event.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=255)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=event.models.avatarupload)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('resolution_date', models.DateTimeField()),
                ('token_volume', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('min_token_stake', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('platform_share', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('event_id', models.IntegerField(blank=True, null=True)),
                ('create_event_tx_receipt', models.CharField(blank=True, max_length=255, null=True)),
                ('update_event_tx_receipt', models.CharField(blank=True, max_length=255, null=True)),
                ('close_event_tx_receipt', models.CharField(blank=True, max_length=255, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='event.category')),
            ],
        ),
        migrations.CreateModel(
            name='PossibleResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.CharField(max_length=255)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='possible_results', to='event.event')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='final_result',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='event.possibleresult'),
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_staked', models.PositiveIntegerField(blank=True, null=True)),
                ('tx_hash', models.CharField(blank=True, max_length=512, null=True)),
                ('amount_rewarded', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.account')),
                ('possible_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event.possibleresult')),
            ],
        ),
    ]

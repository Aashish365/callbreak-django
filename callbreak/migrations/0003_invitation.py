# Generated by Django 5.0.4 on 2024-04-19 04:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callbreak', '0002_remove_roomplayer_is_ready'),
        ('user', '0002_player'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_invitations', to='user.player')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='callbreak.room')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_invitations', to='user.player')),
            ],
        ),
    ]
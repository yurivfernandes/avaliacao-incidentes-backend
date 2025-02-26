# Generated by Django 4.2.10 on 2025-02-26 01:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dw_analytics", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Premissas",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "qtd_incidents",
                    models.IntegerField(
                        help_text="Quantidade de incidentes a serem sorteados"
                    ),
                ),
                ("is_contrato_lancado", models.BooleanField(default=True)),
                ("is_horas_lancadas", models.BooleanField(default=True)),
                ("is_has_met_first_response_target", models.BooleanField(default=True)),
                ("is_resolution_target", models.BooleanField(default=True)),
                ("is_atualizaca_logs_correto", models.BooleanField(default=True)),
                ("is_ticket_encerrado_corretamente", models.BooleanField(default=True)),
                ("is_descricao_troubleshooting", models.BooleanField(default=True)),
                ("is_cliente_notificado", models.BooleanField(default=True)),
                ("is_category_correto", models.BooleanField(default=True)),
                (
                    "assignment",
                    models.OneToOneField(
                        help_text="Assignment Group relacionado",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="premissas",
                        to="dw_analytics.assignmentgroup",
                    ),
                ),
            ],
            options={
                "verbose_name": "Premissa",
                "verbose_name_plural": "Premissas",
                "db_table": "d_premissas",
            },
        ),
    ]

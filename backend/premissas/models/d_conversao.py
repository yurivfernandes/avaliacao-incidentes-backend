from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum


class Conversao(models.Model):
    criterio = models.ForeignKey(
        "Criterios", on_delete=models.CASCADE, related_name="conversoes"
    )
    nome = models.CharField(max_length=100)
    percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        db_table = "d_conversao"
        verbose_name = "Conversão"
        verbose_name_plural = "Conversões"

from access.models import User
from django.contrib.auth import get_user_model
from dw_analytics.models import AssignmentGroup, Contract
from rest_framework import serializers

from ...models import Avaliacao
from .nota_criterio_serializer import (
    NotaCriterioBooleanoSerializer,
    NotaCriterioConversaoSerializer,
)

User = get_user_model()


class AvaliacaoSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source="incident.number")
    resolved_by = serializers.SerializerMethodField()
    assignment_group = serializers.SerializerMethodField()
    contract = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    data_referencia = serializers.SerializerMethodField()
    notas_booleanas = NotaCriterioBooleanoSerializer(
        source="notacriteriobooleano_set", many=True, read_only=True
    )
    notas_conversao = NotaCriterioConversaoSerializer(
        source="notacriterioconversao_set", many=True, read_only=True
    )

    class Meta:
        model = Avaliacao
        fields = [
            "id",
            "incident",
            "number",
            "assignment_group",
            "resolved_by",
            "contract",
            "created_by",
            "user",
            "data_referencia",  # Movido para antes das notas
            "created_at",
            "updated_at",
            "notas_booleanas",
            "notas_conversao",
        ]

    def get_created_by(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return ""

    def get_resolved_by(self, obj):
        try:
            if not obj.incident.resolved_by:
                return ""
            user = User.objects.filter(id=obj.incident.resolved_by).first()
            return (
                f"{user.first_name} {user.last_name}".strip() if user else ""
            )
        except (User.DoesNotExist, ValueError, AttributeError):
            return ""

    def get_assignment_group(self, obj):
        try:
            if not obj.incident.assignment_group:
                return ""
            group = AssignmentGroup.objects.filter(
                id=obj.incident.assignment_group
            ).first()
            return (
                group.dv_assignment_group
                if group
                else obj.incident.assignment_group
            )
        except (AssignmentGroup.DoesNotExist, ValueError):
            return obj.incident.assignment_group

    def get_contract(self, obj):
        try:
            if not obj.incident.contract:
                return ""
            contract = Contract.objects.filter(
                id=obj.incident.contract
            ).first()
            return contract.dv_contract if contract else ""
        except (Contract.DoesNotExist, ValueError):
            return ""

    def get_data_referencia(self, obj):
        try:
            if (
                obj.incident.closed_at
            ):  # Alterado de resolved_at para closed_at
                return obj.incident.closed_at.strftime("%m-%Y")
            return ""
        except AttributeError:
            return ""

    def to_representation(self, instance):
        # Garante que cada avaliação seja serializada apenas uma vez
        representation = super().to_representation(instance)

        # Removemos possíveis duplicatas nas notas
        if "notas_booleanas" in representation:
            seen = set()
            unique_notas = []
            for nota in representation["notas_booleanas"]:
                nota_key = (nota["criterio_nome"], nota["valor"])
                if nota_key not in seen:
                    seen.add(nota_key)
                    unique_notas.append(nota)
            representation["notas_booleanas"] = unique_notas

        if "notas_conversao" in representation:
            seen = set()
            unique_notas = []
            for nota in representation["notas_conversao"]:
                nota_key = (nota["criterio_nome"], nota["valor_convertido"])
                if nota_key not in seen:
                    seen.add(nota_key)
                    unique_notas.append(nota)
            representation["notas_conversao"] = unique_notas

        return representation

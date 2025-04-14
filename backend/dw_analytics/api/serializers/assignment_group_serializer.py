from rest_framework import serializers

from ...models import AssignmentGroup


class AssignmentGroupSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentGroup
        fields = [
            "id",
            "dv_assignment_group",
            "status",
            "empresa",
            "empresa_nome",
        ]

    def get_empresa_nome(self, obj):
        return obj.empresa.nome if obj.empresa else None

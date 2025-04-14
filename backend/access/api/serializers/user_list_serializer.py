from rest_framework import serializers

from ...models import User


class UserListSerializer(serializers.ModelSerializer):
    assignment_groups = serializers.SerializerMethodField()
    empresa_id = serializers.IntegerField(source="empresa.id", allow_null=True)
    empresa = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "full_name",
            "first_name",
            "last_name",
            "assignment_groups",
            "is_staff",
            "is_gestor",
            "is_tecnico",
            "is_ativo",
            "empresa_id",
            "empresa",
        ]

    def get_assignment_groups(self, obj):
        return [
            {
                "id": group.id,
                "dv_assignment_group": group.dv_assignment_group,
            }
            for group in obj.assignment_groups.all()
        ]

    def get_empresa(self, obj):
        return obj.empresa.nome if obj.empresa else None

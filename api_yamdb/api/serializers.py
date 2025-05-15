from rest_framework import serializers

from reviews.models import User


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'role', 'bio'
        )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and not request.user.is_admin:
            fields["role"].read_only = True
        return fields


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True)
    confirmation_code = serializers.CharField(
        required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
from rest_framework import serializers

from .models import Pseudocode


class PseudoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pseudocode
        fields = ["pseudocode"]


class PythonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pseudocode
        fields = ["python_code"]

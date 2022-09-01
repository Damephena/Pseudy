from django.http import HttpResponse
from rest_framework import parsers, status, viewsets
from rest_framework.response import Response

from common.pseudopy import pseudocode_converter

from .models import Pseudocode
from .serializers import PseudoSerializer, PythonSerializer


class PseudoPyViewset(viewsets.ModelViewSet):
    queryset = Pseudocode.objects.all()
    serializer_class = PseudoSerializer
    http_method_names = ["get", "post", "patch"]
    parser_classes = [parsers.JSONParser]

    def get_serializer_class(self):
        if self.action != "create":
            return PythonSerializer
        return super().get_serializer_class()

    def create(self, request):
        serializer = PythonSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            python_code = "\n".join(
                pseudocode_converter(request.data.get("pseudocode"))
            )
            serializer.save(python_code=python_code)
            return HttpResponse(
                python_code, status=status.HTTP_201_CREATED, content_type="text/plain"
            )
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

from django.db import models


class Pseudocode(models.Model):
    pseudocode = models.TextField()
    python_code = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

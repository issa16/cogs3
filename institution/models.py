from django.db import models


class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

from django.db import models


class System(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=512)
    number_of_cores = models.PositiveIntegerField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

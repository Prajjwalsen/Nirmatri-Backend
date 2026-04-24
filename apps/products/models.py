from django.db import models

class Product(models.Model):

    name = models.CharField(max_length=200)

    description = models.TextField()

    price = models.FloatField()

    category = models.CharField(max_length=100)

    image = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
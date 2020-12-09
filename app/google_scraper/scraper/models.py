import json

from django.db import models


class Results(models.Model):
    ip = models.GenericIPAddressField()
    query = models.CharField(
        max_length=200,
    )
    number_of_results = models.PositiveBigIntegerField(
        null=True
    )
    links = models.JSONField()
    top_words = models.JSONField()
    results_limitation = models.PositiveSmallIntegerField(
        null=True
    )
    top_words_number = models.PositiveSmallIntegerField(
        null=True
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
    )
    modified_date = models.DateTimeField(
        auto_now=True,
    )


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class Location(models.Model):
    """
    A predefined location of interest for weather forecasts
    """

    name = models.CharField(max_length=50)
    latitude = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("location", kwargs={"pk": self.pk})

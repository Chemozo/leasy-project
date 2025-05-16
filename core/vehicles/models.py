from django.db import models


class VehicleBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    brand = models.ForeignKey(
        VehicleBrand, on_delete=models.CASCADE, related_name="models"
    )
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("brand", "name")

    def __str__(self):
        return f"{self.brand} {self.name}"


class Vehicle(models.Model):
    brand = models.ForeignKey(VehicleBrand, on_delete=models.PROTECT)
    model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT)
    license_plate = models.CharField(max_length=10, unique=True)
    vin = models.CharField(max_length=17, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.license_plate})"

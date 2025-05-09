# contracts/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from clients.models import Client
from vehicles.models import Vehicle


class Contract(models.Model):
    class BillingCycle(models.TextChoices):
        WEEKLY = "weekly", _("Weekly")
        BIWEEKLY = "biweekly", _("Bi-weekly")
        MONTHLY = "monthly", _("Monthly")

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="contracts"
    )
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="contracts"
    )
    billing_cycle = models.CharField(
        max_length=10, choices=BillingCycle.choices, default=BillingCycle.MONTHLY
    )
    active = models.BooleanField(default=True)
    installment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["client"],
                condition=models.Q(active=True),
                name="unique_active_client_contract",
            ),
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=models.Q(active=True),
                name="unique_active_vehicle_contract",
            ),
        ]
        ordering = ["-start_date"]

    def clean(self):
        """Validate no existing active contracts for client/vehicle"""
        super().clean()

        if self.active:
            client_conflict = (
                Contract.objects.filter(client=self.client, active=True)
                .exclude(pk=self.pk)
                .exists()
            )

            if client_conflict:
                raise ValidationError(
                    _("This client already has an active contract"),
                    code="client_conflict",
                )

            # Check for existing active vehicle contract (exclude self if updating)
            vehicle_conflict = (
                Contract.objects.filter(vehicle=self.vehicle, active=True)
                .exclude(pk=self.pk)
                .exists()
            )

            if vehicle_conflict:
                raise ValidationError(
                    _("This vehicle already has an active contract"),
                    code="vehicle_conflict",
                )

    def save(self, *args, **kwargs):
        """Enforce validation before saving"""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Contract #{self.id} - {self.client} ({self.get_billing_cycle_display()})"
        )

from django.db import models
from django.core.validators import MinValueValidator
from contracts.models import Contract
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class Invoice(models.Model):
    class StatusChoices(models.TextChoices):
        PAID = "paid", "Paid"
        PENDING = "pending", "Pending"
        OVERDUE = "overdue", "Overdue"

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    issue_date = models.DateField(
        auto_now_add=True,
    )
    period_end = models.DateField()
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    status = models.CharField(
        max_length=7,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-period_end"]
        constraints = [
            models.UniqueConstraint(
                fields=["contract", "period_end"], name="unique_invoice_per_period"
            )
        ]
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

    def __str__(self):
        return f"Factura {self.id} - {self.contract.client} ({self.period_end})"

    def save(self, *args, **kwargs):
        """Actualización automática de estado"""
        if self.payment_date:
            self.status = self.StatusChoices.PAID
        elif self.period_end < timezone.now().date():
            self.status = self.StatusChoices.OVERDUE
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return (
            self.period_end < timezone.now().date()
            and self.status != self.StatusChoices.PAID
        )

    @classmethod
    def calculate_period_end(cls, period_end, billing_cycle):
        """Calcula la fecha de vencimiento según el ciclo de facturación usando relativedelta"""
        if billing_cycle == "weekly":
            return period_end + relativedelta(weeks=1)
        elif billing_cycle == "biweekly":
            return period_end + relativedelta(weeks=2)
        elif billing_cycle == "monthly":
            return period_end + relativedelta(months=1, day=1)
        else:
            return period_end

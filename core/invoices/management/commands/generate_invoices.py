# invoices/management/commands/generate_invoices.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from contracts.models import Contract
from invoices.models import Invoice
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar


class Command(BaseCommand):

    def handle(self, *args, **options):

        for contract in Contract.objects.filter(active=True):
            last_invoice = contract.invoices.order_by("-period_end").first()

            period_info = self.calculate_billing_period(
                contract.start_date,
                contract.billing_cycle,
                last_invoice.period_end if last_invoice else None,
            )

            # Skip if invoice already exists for this period
            if Invoice.objects.filter(
                contract=contract, period_end=period_info["period_end"]
            ).exists():
                self.stdout.write(
                    f"Skipping existing invoice for {contract} ({period_info['period_end']})"
                )
                continue

            amount = self.prorate_amount(
                contract.installment_amount,
                period_info["days_in_period"],
                period_info["days_covered"],
            )

            Invoice.objects.create(
                contract=contract,
                period_end=period_info["period_end"],
                due_date=period_info["due_date"],
                amount=amount,
            )
            self.stdout.write(
                f"Created invoice for {contract} ({period_info['period_end']})"
            )

    def calculate_billing_period(self, start_date, billing_cycle, last_period_end=None):
        """Returns period_start, period_end, due_date, and days covered"""
        if not last_period_end:
            return self._calculate_first_period(start_date, billing_cycle)

        return self._calculate_regular_period(last_period_end, billing_cycle)

    def _calculate_first_period(self, start_date, billing_cycle):
        if billing_cycle == "weekly":
            period_start = start_date - timedelta(days=start_date.weekday())
            period_end = period_start + timedelta(days=6)
            due_date = period_start + timedelta(days=10)

        elif billing_cycle == "biweekly":
            if start_date.day <= 14:
                period_start = start_date.replace(day=1)
                period_end = start_date.replace(day=14)
            else:
                period_start = start_date.replace(day=15)
                period_end = start_date.replace(
                    day=calendar.monthrange(start_date.year, start_date.month)[1]
                )
            # Set due_date to the 15th of the next month
            next_month = period_end.replace(day=1) + relativedelta(months=1)
            due_date = next_month.replace(day=15)

        else:  # monthly
            period_start = start_date.replace(day=1)
            period_end = period_start + relativedelta(months=1) - timedelta(days=1)
            due_date = period_end + timedelta(days=1)

        days_in_period = (period_end - period_start).days + 1
        days_covered = (start_date - period_start).days + 1

        return {
            "period_start": period_start,
            "period_end": period_end,
            "due_date": due_date,
            "days_in_period": days_in_period,
            "days_covered": days_covered,
        }

    def _calculate_regular_period(self, last_period_end, billing_cycle):
        if billing_cycle == "weekly":
            period_start = last_period_end + timedelta(days=1)
            period_end = period_start + timedelta(days=6)
            due_date = period_start + timedelta(days=10)

        elif billing_cycle == "biweekly":
            if last_period_end.day == 14:
                period_start = last_period_end + timedelta(days=1)
                period_end = period_start.replace(
                    day=calendar.monthrange(period_start.year, period_start.month)[1]
                )
            else:
                period_start = last_period_end + timedelta(days=1)
                period_end = period_start.replace(day=14)
            # Set due_date to the 15th of the next month
            next_month = period_end.replace(day=1) + relativedelta(months=1)
            due_date = next_month.replace(day=15)

        else:  # monthly
            period_start = last_period_end + timedelta(days=1)
            period_end = period_start + relativedelta(months=1) - timedelta(days=1)
            due_date = period_end + timedelta(days=1)

        return {
            "period_start": period_start,
            "period_end": period_end,
            "due_date": due_date,
            "days_in_period": (period_end - period_start).days + 1,
            "days_covered": (period_end - period_start).days + 1,
        }

    def prorate_amount(self, full_amount, total_days, covered_days):
        if total_days == covered_days:
            return full_amount
        return round((full_amount / total_days) * covered_days, 2)

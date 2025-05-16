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

            if last_invoice and last_invoice.period_end >= timezone.now().date():
                self.stdout.write(
                    f"Skipping contract {contract} (last invoice period_end: {last_invoice.period_end})"
                )
                continue
            today = timezone.now().date()
            period_info = self.calculate_billing_period(
                today,
                contract.billing_cycle,
                last_invoice.period_end if last_invoice else None,
            )

            amount = self.prorate_amount(
                contract.installment_amount,
                period_info["days_in_period"],
                period_info["days_covered"],
            )

            Invoice.objects.create(
                contract=contract,
                period_end=period_info["period_end"],
                amount=amount,
            )
            self.stdout.write(
                f"Created invoice for {contract} ({period_info['period_end']})"
            )

    def calculate_billing_period(self, start_date, billing_cycle, last_period_end=None):
        """Returns period_start, period_end, and days covered"""
        if not last_period_end:
            return self._calculate_first_period(start_date, billing_cycle)

        return self._calculate_regular_period(last_period_end, billing_cycle)

    def _calculate_first_period(self, start_date, billing_cycle):
        if billing_cycle == "weekly":
            # End on the next Monday (weekday=0)
            period_start = start_date
            days_until_monday = (7 - start_date.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            period_end = start_date + timedelta(days=days_until_monday)

        elif billing_cycle == "biweekly":
            # 1-15 or 16-end of month
            if start_date.day <= 15:
                period_start = start_date.replace(day=1)
                period_end = start_date.replace(day=15)
            else:
                period_start = start_date.replace(day=16)
                last_day = calendar.monthrange(start_date.year, start_date.month)[1]
                period_end = start_date.replace(day=last_day)

        else:  # monthly
            # End on the 1st of next month
            period_start = start_date.replace(day=1)
            period_end = (period_start + relativedelta(months=1)).replace(day=1)

        days_in_period = (period_end - period_start).days + 1
        days_covered = days_in_period

        return {
            "period_start": period_start,
            "period_end": period_end,
            "days_in_period": days_in_period,
            "days_covered": days_covered,
        }

    def _calculate_regular_period(self, last_period_end, billing_cycle):
        if billing_cycle == "weekly":
            period_start = last_period_end + timedelta(days=1)
            days_until_monday = (7 - period_start.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            period_end = period_start + timedelta(days=days_until_monday)

        elif billing_cycle == "biweekly":
            if last_period_end.day == 15:
                period_start = last_period_end + timedelta(days=1)
                last_day = calendar.monthrange(period_start.year, period_start.month)[1]
                period_end = period_start.replace(day=last_day)
            else:
                period_start = last_period_end + timedelta(days=1)
                period_end = period_start.replace(day=15)

        else:  # monthly
            period_start = (last_period_end + timedelta(days=1)).replace(day=1)
            period_end = (period_start + relativedelta(months=1)).replace(day=1)

        days_in_period = (period_end - period_start).days + 1
        days_covered = days_in_period

        return {
            "period_start": period_start,
            "period_end": period_end,
            "days_in_period": days_in_period,
            "days_covered": days_covered,
        }

    def prorate_amount(self, full_amount, total_days, covered_days):
        if total_days == covered_days:
            return full_amount
        return round((full_amount / total_days) * covered_days, 2)

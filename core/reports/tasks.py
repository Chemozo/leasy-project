import openpyxl
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings


def generate_report_task(user_email, selected_columns, data):
    # Create Excel file
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(selected_columns)

    for row in data:
        ws.append([row.get(col, "") for col in selected_columns])

    # Save to in-memory file
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    # Send email with attachment
    email = EmailMessage(
        subject="Your Report is Ready",
        body="Please find the attached report.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )
    email.attach(
        f"report_{user_email}.xlsx",
        buffer.getvalue(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    try:
        email.send()
    except Exception as e:
        print(e)

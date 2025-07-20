import pandas as pd
from celery import shared_task
from .models import Customer, Loan
from datetime import datetime

@shared_task
def ingest_customers_from_excel():
    df = pd.read_excel('customer_data.xlsx')
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            phone_number=str(row['Phone Number']),
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'monthly_salary': row['Monthly Salary'],
                'approved_limit': row['Approved Limit'],
                'current_debt': 0.0,  # Not present in Excel, set to 0
                'age': row.get('Age', 0),
            }
        )

@shared_task
def ingest_loans_from_excel():
    df = pd.read_excel('loan_data.xlsx')
    for _, row in df.iterrows():
        try:
            customer = Customer.objects.get(id=row['Customer ID'])
        except Customer.DoesNotExist:
            continue
        Loan.objects.update_or_create(
            id=row['Loan ID'],
            defaults={
                'customer': customer,
                'loan_amount': row['Loan Amount'],
                'tenure': row['Tenure'],
                'interest_rate': row['Interest Rate'],
                'monthly_installment': row['Monthly payment'],
                'emis_paid_on_time': row['EMIs paid on Time'],
                'start_date': pd.to_datetime(row['Date of Approval']).date() if not pd.isnull(row['Date of Approval']) else datetime.now().date(),
                'end_date': pd.to_datetime(row['End Date']).date() if not pd.isnull(row['End Date']) else datetime.now().date(),
                'repayments_left': max(0, row['Tenure'] - row['EMIs paid on Time'])
            }
        ) 
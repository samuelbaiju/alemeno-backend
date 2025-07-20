from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit', 'current_debt']

class LoanSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'customer', 'loan_amount', 'tenure', 'interest_rate', 'monthly_installment', 'emis_paid_on_time', 'start_date', 'end_date', 'repayments_left'] 
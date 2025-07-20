from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import datetime
import math

class RegisterView(APIView):
    def post(self, request):
        data = request.data.copy()
        monthly_salary = int(data.get('monthly_income', 0))
        approved_limit = int(round(36 * monthly_salary, -5))
        customer = Customer.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            phone_number=data['phone_number'],
            monthly_salary=monthly_salary,
            approved_limit=approved_limit,
        )
        serializer = CustomerSerializer(customer)
        resp = serializer.data
        resp['name'] = f"{customer.first_name} {customer.last_name}"
        resp['monthly_income'] = customer.monthly_salary
        return Response(resp, status=status.HTTP_201_CREATED)

class CheckEligibilityView(APIView):
    def post(self, request):
        data = request.data
        customer = get_object_or_404(Customer, id=data['customer_id'])
        loan_amount = float(data['loan_amount'])
        interest_rate = float(data['interest_rate'])
        tenure = int(data['tenure'])
        # Credit score calculation
        loans = Loan.objects.filter(customer=customer)
        total_current_loans = loans.aggregate(total=Sum('loan_amount'))['total'] or 0
        if total_current_loans + loan_amount > customer.approved_limit:
            credit_score = 0
        else:
            paid_on_time = sum([l.emis_paid_on_time for l in loans])
            num_loans = loans.count()
            current_year = datetime.now().year
            loans_this_year = loans.filter(start_date__year=current_year).count()
            approved_volume = total_current_loans
            credit_score = min(100, paid_on_time * 5 + num_loans * 10 + loans_this_year * 10 + approved_volume // 100000)
        # Approval logic
        approval = False
        corrected_interest_rate = interest_rate
        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                approval = True
            else:
                corrected_interest_rate = 13.0
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                approval = True
            else:
                corrected_interest_rate = 17.0
        else:
            approval = False
        # EMI calculation
        r = (corrected_interest_rate / 100) / 12
        emi = (loan_amount * r * (1 + r) ** tenure) / ((1 + r) ** tenure - 1) if r > 0 else loan_amount / tenure
        # Check EMI to salary ratio
        if emi > 0.5 * customer.monthly_salary:
            approval = False
        resp = {
            'customer_id': customer.id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': round(emi, 2)
        }
        return Response(resp, status=status.HTTP_200_OK)

class CreateLoanView(APIView):
    def post(self, request):
        data = request.data
        customer = get_object_or_404(Customer, id=data['customer_id'])
        # Reuse eligibility logic
        eligibility_view = CheckEligibilityView()
        eligibility_resp = eligibility_view.post(request).data
        if not eligibility_resp['approval']:
            return Response({
                'loan_id': None,
                'customer_id': customer.id,
                'loan_approved': False,
                'message': 'Loan not approved',
                'monthly_installment': eligibility_resp['monthly_installment']
            }, status=status.HTTP_200_OK)
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=data['loan_amount'],
            tenure=data['tenure'],
            interest_rate=eligibility_resp['corrected_interest_rate'],
            monthly_installment=eligibility_resp['monthly_installment'],
            emis_paid_on_time=0,
            start_date=datetime.now().date(),
            end_date=datetime.now().date(),
            repayments_left=data['tenure']
        )
        return Response({
            'loan_id': loan.id,
            'customer_id': customer.id,
            'loan_approved': True,
            'message': 'Loan approved',
            'monthly_installment': loan.monthly_installment
        }, status=status.HTTP_201_CREATED)

class ViewLoanView(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, id=loan_id)
        customer = loan.customer
        resp = {
            'loan_id': loan.id,
            'customer': {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'phone_number': customer.phone_number,
                'age': customer.age
            },
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_installment,
            'tenure': loan.tenure
        }
        return Response(resp, status=status.HTTP_200_OK)

class ViewLoansByCustomerView(APIView):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        loans = Loan.objects.filter(customer=customer)
        resp = []
        for loan in loans:
            resp.append({
                'loan_id': loan.id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_installment,
                'repayments_left': loan.repayments_left
            })
        return Response(resp, status=status.HTTP_200_OK)

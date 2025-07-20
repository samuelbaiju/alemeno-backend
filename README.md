# Alemno Credit Approval System

A full-stack backend system for credit/loan approval, built with Django, Django Rest Framework, Celery, PostgreSQL, Redis, and Docker. This project supports background ingestion of customer and loan data from Excel, robust API endpoints for customer and loan management, and is fully dockerized for easy deployment.

---

## Features
- Customer registration and approved limit calculation
- Loan eligibility check and credit score calculation
- Loan creation and management
- View individual loans and all loans for a customer
- Background ingestion of Excel data (customers and loans) via Celery
- PostgreSQL database
- Redis as Celery broker
- Fully dockerized (run everything with one command)
- Error handling and logging

---

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/)

### Clone the Repository
```sh
git clone https://github.com/samuelbaiju/alemeno-backend.git
cd alemno-credit
```

### Build and Run All Services
```sh
docker-compose up --build
```
This will start:
- Django web server
- Celery worker
- PostgreSQL database
- Redis broker

### Apply Migrations (if needed)
```sh
docker-compose exec web python /app/credit_system/manage.py migrate
```

### Ingest Excel Data (optional)
```sh
docker-compose exec web python /app/credit_system/manage.py shell -c "from credit_system.core.tasks import ingest_customers_from_excel, ingest_loans_from_excel; ingest_customers_from_excel(); ingest_loans_from_excel()"
```

---

## API Endpoints

### 1. Register a New Customer
- **POST** `/register`
- **Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "phone_number": "1234567890",
  "monthly_income": 50000
}
```
- **Response:** Customer details with approved limit.

---

### 2. Check Loan Eligibility
- **POST** `/check-eligibility`
- **Request Body:**
```json
{
  "customer_id": 301,
  "loan_amount": 100000,
  "interest_rate": 12.0,
  "tenure": 12
}
```
- **Response:** Eligibility status, corrected interest rate, and monthly installment.

---

### 3. Create a Loan
- **POST** `/create-loan`
- **Request Body:**
```json
{
  "customer_id": 301,
  "loan_amount": 100000,
  "interest_rate": 12.0,
  "tenure": 12
}
```
- **Response:** Loan approval status and details.

---

### 4. View a Specific Loan
- **GET** `/view-loan/<loan_id>`
- **Example:** `/view-loan/1`
- **Response:** Loan and customer details.

---

### 5. View All Loans for a Customer
- **GET** `/view-loans/<customer_id>`
- **Example:** `/view-loans/301`
- **Response:** List of all loans for the customer.

---

## Example Usage (with curl)

**Register a customer:**
```sh
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "age": 30, "phone_number": "1234567890", "monthly_income": 50000}'
```

**Check eligibility:**
```sh
curl -X POST http://localhost:8000/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 301, "loan_amount": 100000, "interest_rate": 12.0, "tenure": 12}'
```

**Create a loan:**
```sh
curl -X POST http://localhost:8000/create-loan \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 301, "loan_amount": 100000, "interest_rate": 12.0, "tenure": 12}'
```

**View a loan:**
```sh
curl http://localhost:8000/view-loan/1
```

**View all loans for a customer:**
```sh
curl http://localhost:8000/view-loans/301
```

---

## Project Structure
```
alemeno-credit/
├── credit_system/           # Django project and app code
│   ├── core/                # Main app: models, views, tasks, etc.
│   └── ...
├── customer_data.xlsx       # Excel data for customers
├── loan_data.xlsx           # Excel data for loans
├── Dockerfile               # Docker build for Django app
├── docker-compose.yml       # Orchestrates all services
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## Notes
- All endpoints require JSON bodies for POST requests.
- Make sure to run migrations and ingest Excel data before using the APIs.
- If you ingest new Excel data, reset the sequence for customer IDs as described in troubleshooting.

---

## Troubleshooting
- **Duplicate key error:** Reset the sequence with:
  ```sh
  docker-compose exec db psql -U postgres -d credit_db -c "SELECT setval(pg_get_serial_sequence('core_customer', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM core_customer;"
  ```
- **Celery worker not running:** Make sure the worker service is up in Docker Compose.
- **Database errors:** Ensure migrations are applied and the database is running.

---

## Running the Project with Docker

### 1. Build and Start All Services
Run this command from the project root:
```sh
docker-compose up --build
```
This will build the images (if needed) and start:
- Django web server (API)
- Celery worker (background tasks)
- PostgreSQL database
- Redis broker

### 2. Access the API
- By default, the Django API will be available at: [http://localhost:8000](http://localhost:8000)
- You can test endpoints using Postman, curl, or your browser (for GET requests).

### 3. Stopping the Project
To stop all running containers:
```sh
docker-compose down
```

### 4. Running in the Background (Detached Mode)
```sh
docker-compose up -d --build
```
To stop:
```sh
docker-compose down
```

### 5. Running Management Commands
To run Django management commands (like migrations or shell):
```sh
docker-compose exec web python /app/credit_system/manage.py <command>
```
Example:
```sh
docker-compose exec web python /app/credit_system/manage.py migrate
```

---

 
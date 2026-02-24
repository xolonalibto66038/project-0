# Django Stripe Payment App

A Django web application with Stripe subscription integration. This project demonstrates how to implement Stripe Checkout, manage subscriptions, handle webhooks, and deploy using Render with PostgreSQL.

---

# Features

* Stripe Checkout integration
* Subscription management
* Stripe webhook handling
* PostgreSQL support (production)
* Local development support (SQLite/PostgreSQL)
* Production deployment with Render
* Secure environment variable configuration

---

# Tech Stack

* Python 3.10+
* Django 5+
* Stripe API
* PostgreSQL
* Render (deployment)
* Gunicorn + Uvicorn
* python-dotenv

---

# Project Structure

```
project-0/
│
├── .venv/
├── requirements.txt
├── build.sh
├── render.yaml
├── .env
│
└── src/
    ├── manage.py
    ├── static/
    │   └── main.js
    ├── templates/
    │   ├── cancel.html
    │   ├── dashboard.html
    │   ├── hone.html
    │   └── success.html
    ├── core/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    │
    └── billing/
        ├── models.py
        ├── views.py
        ├── decorators.py
        ├── webhooks.py
        ├── urls.py
        └── services.py
```

---

# Environment Variables

Create a `.env` file in the project root (same level as `requirements.txt`):

```
SECRET_KEY=your_django_secret_key

DATABASE_URL=sqlite:///db.sqlite3

STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID=price_...
STRIPE_ENDPOINT_SECRET=whsec_...
```

---

# Stripe Setup (Test Mode)

Go to Stripe Dashboard:

https://dashboard.stripe.com/test/dashboard

Make sure Test Mode is enabled.

---

## 1. Get API Keys

Go to:

Developers → API Keys

Copy:

```
STRIPE_PUBLISHABLE_KEY = pk_test_...
STRIPE_SECRET_KEY = sk_test_...
```

---

## 2. Create Product and Price

Go to:

Products → Create Product

Example:

* Name: Premium Plan
* Price: $10/month
* Billing period: Monthly

After creation, copy:

```
STRIPE_PRICE_ID = price_...
```

---

## 3. Create Webhook

Go to:

Developers → Webhooks → Add endpoint

Endpoint URL (local):

```
http://127.0.0.1:8000/webhook/
```

Events to listen:

```
checkout.session.completed
customer.subscription.updated
customer.subscription.deleted
invoice.payment_succeeded
invoice.payment_failed
```

Copy:

```
STRIPE_ENDPOINT_SECRET = whsec_...
```

---

# Local Development Setup

## 1. Clone repository

```
git clone https://github.com/yourusername/project-0.git
cd project-0
```

---

## 2. Create virtual environment

```
python -m venv .venv
source .venv/bin/activate
```

Windows:

```
.venv\Scripts\activate
```

---

## 3. Install dependencies

```
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create `.env` file as described above.

---

## 5. Run migrations

```
cd src
python manage.py migrate
```

---

## 6. Create superuser

```
python manage.py createsuperuser
```

---

## 7. Run server

```
python manage.py runserver
```

Visit:

```
http://127.0.0.1:8000
```

Admin:

```
http://127.0.0.1:8000/admin
```

---

# Stripe Webhook Local Testing (Recommended)

Install Stripe CLI:

https://stripe.com/docs/stripe-cli

Login:

```
stripe login
```

Forward webhooks:

```
stripe listen --forward-to localhost:8000/webhook/
```

Copy generated webhook secret into `.env`.

---

# Production Deployment (Render)

---

# Step 1: Push to GitHub

```
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/project-0.git
git push -u origin main
```

---

# Step 2: Create Render Account

https://render.com/

---

# Step 3: Create PostgreSQL Database

Render Dashboard → New → PostgreSQL

Example:

```
Name: project0db
Plan: Free
```

Copy Internal Database URL.

---

# Step 4: Create Web Service

Render Dashboard → New → Web Service

Connect your GitHub repository.

Settings:

```
Runtime: Python

Build Command:
./build.sh

Start Command:
cd src && python -m gunicorn core.asgi:application -k uvicorn.workers.UvicornWorker
```

---

# Step 5: Add Environment Variables in Render

Render → Web Service → Environment

Add:

```
SECRET_KEY=your_secret_key

DATABASE_URL=postgresql://...

STRIPE_PUBLISHABLE_KEY=pk_test_...

STRIPE_SECRET_KEY=sk_test_...

STRIPE_PRICE_ID=price_...

STRIPE_ENDPOINT_SECRET=whsec_...
```

---

# Step 6: Configure Stripe Webhook (Production)

Stripe Dashboard → Webhooks → Add endpoint

Endpoint URL:

```
https://your-app-name.onrender.com/webhook/
```

Select same events:

```
checkout.session.completed
customer.subscription.updated
customer.subscription.deleted
invoice.payment_succeeded
invoice.payment_failed
```

Copy secret and update Render environment variable.

---

# Step 7: Apply migrations in Render Shell

Render → Web Service → Shell

```
cd src
python manage.py migrate
python manage.py createsuperuser
```

---

# build.sh Example

```
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

cd src

python manage.py collectstatic --noinput
python manage.py migrate
```

---

# Production Settings Example

In settings.py:

```
DEBUG = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]
```

---

# Test Stripe Payments

Use test card:

```
4242 4242 4242 4242
12/34
123
```

---

# License

MIT License

---

# Author

xolon alibto

---

# Support

If you encounter issues, check:

* Stripe logs
* Render logs
* Django logs

---

# Summary

This project demonstrates a full Stripe subscription integration with Django and production deployment using Render and PostgreSQL.

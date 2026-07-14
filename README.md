# FarmLink Marketplace 

A Direct Farmer-to-Consumer Marketplace Backend built with FastAPI and PostgreSQL.

## Project Overview

FarmLink is a marketplace platform that connects farmers directly with consumers, eliminating intermediaries and ensuring fair prices for both parties. Farmers can list their agricultural products, while consumers can browse, add to cart, place orders, and leave reviews.

## Features

- **User Authentication**: Secure registration and login with JWT tokens
- **Product Management**: Farmers can create, update, and delete their product listings
- **Shopping Cart**: Add, update, and remove items from cart with real-time price calculation
- **Order Management**: Place orders and track order status (pending, confirmed, shipped, delivered, cancelled)
- **Product Reviews**: 1-5 star rating system with comments (one review per user per product)
- **Role-Based Access Control**: Separate permissions for farmers and consumers
- **API Documentation**: Interactive Swagger UI at `/docs`

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.10+** - Programming language
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation using Python type annotations
- **JWT (PyJWT)** - Authentication token generation and validation
- **bcrypt** - Secure password hashing
- **uvicorn** - ASGI server for running FastAPI

## Project Structure

```
Farmlink_backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Application configuration (env variables)
│   ├── database.py             # Database connection and session management
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py            # User model (authentication, roles)
│   │   ├── product.py         # Product model (farmer listings)
│   │   ├── cart.py            # Cart model (shopping cart)
│   │   ├── order.py           # Order model (order tracking)
│   │   └── review.py          # Review model (product ratings)
│   ├── schemas/               # Pydantic validation schemas
│   │   ├── user.py            # User request/response schemas
│   │   ├── product.py         # Product validation schemas
│   │   ├── cart.py            # Cart validation schemas
│   │   ├── order.py           # Order validation schemas
│   │   └── review.py          # Review validation schemas
│   ├── routers/               # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── products.py        # Product CRUD endpoints
│   │   ├── cart.py            # Cart management endpoints
│   │   ├── orders.py          # Order management endpoints
│   │   └── reviews.py         # Review management endpoints
│   ├── services/              # Business logic services
│   │   ├── password_service.py  # Password hashing/verification
│   │   └── auth_service.py      # JWT token generation/validation
│   └── utils/                 # Utility functions
│       └── dependencies.py    # FastAPI dependencies (auth, roles)
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (not in git)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```



## Getting Started

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <https://github.com/gayatri-sharma04/Farmlink.git>
   cd Farmlink_backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root: 
5. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb farmlink
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE farmlink;
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Swagger Documentation: `http://localhost:8000/docs`
   - ReDoc Documentation: `http://localhost:8000/redoc`

## Security

- **Password Hashing**: All passwords are hashed using bcrypt before storage
- **JWT Authentication**: Secure token-based authentication with 60-minute expiration
- **Role-Based Access Control**: Farmers and consumers have different permissions
- **Input Validation**: All API inputs are validated using Pydantic schemas
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection attacks
- **CORS Configured**: Cross-Origin Resource Sharing properly configured


## About This Project

This is a solo capstone project by Gayatri Sharma developed as a part of academic curriculum,demonstrating full-stack API development, database design, authentication & security, Swagger documentation, and professional coding standards.



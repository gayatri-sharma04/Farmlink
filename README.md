# FarmLink Marketplace – Capstone Project (Backend API)

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

## Database Schema

### Users Table
Stores user accounts with role-based access.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| email | String(255) | Unique email address |
| password_hash | String(255) | Bcrypt hashed password |
| full_name | String(255) | User's full name |
| role | String | "farmer" or "consumer" |
| phone | String(20) | Optional phone number |
| address | Text | Optional address |
| is_active | Boolean | Account status |
| created_at | DateTime | Account creation timestamp |
| updated_at | DateTime | Last update timestamp |

### Products Table
Stores product listings created by farmers.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| name | String(255) | Product name |
| description | Text | Product description |
| price | Numeric(10,2) | Unit price |
| quantity | Integer | Available quantity |
| category | Enum | vegetables, fruits, grains, dairy, other |
| farmer_id | UUID | Foreign key to users.id |
| image_url | String(500) | Optional product image |
| is_available | Boolean | Product availability |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### Carts Table
Stores shopping carts (one per user).

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users.id (unique) |
| items | JSON | List of {product_id, quantity, price} |
| total_price | Numeric(12,2) | Total cart value |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### Orders Table
Stores customer orders.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users.id |
| items | JSON | List of {product_id, quantity, price} |
| total_price | Numeric(12,2) | Total order value |
| status | Enum | pending, confirmed, shipped, delivered, cancelled |
| delivery_address | Text | Delivery location |
| notes | Text | Special instructions |
| created_at | DateTime | Order placement timestamp |
| updated_at | DateTime | Last update timestamp |

### Reviews Table
Stores product reviews and ratings.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users.id |
| product_id | UUID | Foreign key to products.id |
| rating | Integer | Rating (1-5) |
| comment | Text | Optional review text |
| created_at | DateTime | Review creation timestamp |
| updated_at | DateTime | Last update timestamp |

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login and get JWT token | No |

### Products
| Method | Endpoint | Description | Auth Required | Role |
|--------|----------|-------------|---------------|------|
| GET | `/products` | List all products (paginated) | No | - |
| POST | `/products` | Create new product | Yes | Farmer |
| GET | `/products/{id}` | Get product details | No | - |
| PUT | `/products/{id}` | Update product | Yes | Farmer (owner) |
| DELETE | `/products/{id}` | Delete product | Yes | Farmer (owner) |

### Cart
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/cart` | Get current user's cart | Yes |
| POST | `/cart/items` | Add item to cart | Yes |
| PUT | `/cart/items/{product_id}` | Update item quantity | Yes |
| DELETE | `/cart/items/{product_id}` | Remove item from cart | Yes |
| DELETE | `/cart` | Clear entire cart | Yes |

### Orders
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/orders` | Place new order | Yes |
| GET | `/orders` | Get user's orders (paginated) | Yes |
| GET | `/orders/{id}` | Get order details (owner only) | Yes |
| PUT | `/orders/{id}` | Update order status | Yes |

### Reviews
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/reviews` | Create product review | Yes |
| GET | `/reviews/product/{product_id}` | Get product reviews (paginated) | No |
| GET | `/reviews/{id}` | Get review details | No |
| PUT | `/reviews/{id}` | Update review (owner only) | Yes |
| DELETE | `/reviews/{id}` | Delete review (owner only) | Yes |

## Getting Started

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
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
   ```env
   DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/farmlink
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

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

## Project Status

**Completion: 85%**

### Completed
- User authentication system with JWT
- Product CRUD operations with farmer-only access
- Shopping cart with real-time price calculation
- Order placement and status tracking
- Product review system with ratings
- Role-based access control
- API documentation with Swagger UI
- Database schema design
- Input validation with Pydantic

### In Progress
- Frontend integration (React)
- Advanced search and filtering
- Payment gateway integration

## About This Project

This is a solo capstone project by Gayatri Sharma developed as a part of academic curriculum,demonstrating full-stack API development, database design, authentication & security, Swagger documentation, and professional coding standards.



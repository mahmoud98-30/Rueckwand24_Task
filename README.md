# Backend Test Task - FastAPI + MySQL

A complete FastAPI application with JWT authentication, CRUD operations, and image processing to PDF functionality.

## Features

- ✅ **JWT-based Authentication** (login/logout)
- ✅ **User Management** (Full CRUD)
- ✅ **Materials Management** (Full CRUD)
- ✅ **Product Types Management** (Full CRUD)
- ✅ **Item Configuration** with automatic image cropping to PDF
- ✅ **MySQL Database** with async support
- ✅ **Docker Environment**
- ✅ **Unit Tests**

## Project Structure

```
.
Rueckwand24_Task/
├── app/
│   ├── assets/
│   │   └── source.jpg
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── items.py
│   │   ├── materials.py
│   │   ├── product_types.py
│   │   ├── token_sessions.py
│   │   └── users.py
│   ├── storage/
│   │   └── pdfs/
│   ├── test/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_item.py
│   │   ├── test_materials.py
│   │   ├── test_product_type.py
│   │   ├── test_token_sessions.py
│   │   └── test_user.py
│   ├── auth.py
│   ├── database.py
│   ├── image_processor.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── .dockerignore
├── .env
├── .gitignore
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md

```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

## Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/mahmoud98-30/Rueckwand24_Task.git
cd Rueckwand24_Task
```

---

### 2️⃣ Static Assets

The required static image for cropping and PDF generation is **already included** in the project:

```text
app/assets/source.jpg
```

⚠️ **Do not rename or remove this file**, as it is used by the image processing logic.

---

### 3️⃣ Build and Start the Application

```bash
docker compose up --build
```

Or run in detached mode:

```bash
docker compose up -d --build
```

Docker will automatically:

- Build the FastAPI application  
- Start the database service  
- Create database tables on startup  

---

### 4️⃣ Access the Application

Once running, the API is available at:

- **API Base URL**: http://localhost:8000  
- **Swagger UI**: http://localhost:8000/docs  
- **ReDoc**: http://localhost:8000/redoc  

---

### 5️⃣ Running Tests (Inside Docker)

All unit tests are executed inside the application container:

```bash
docker compose exec app python -m pytest
```

Run a specific test file:

```bash
docker compose exec app python -m pytest app/test/test_items.py
```

---

### 6️⃣ Stopping the Application

```bash
docker compose down
```

To also remove volumes (⚠️ deletes database data):

```bash
docker compose down -v
```


## API Usage

### 1. Create a User

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Save the `access_token` from the response.

### 3. Use Authenticated Endpoints

```bash
# Set your token
TOKEN="your-access-token-here"

# Create a material
curl -X POST http://localhost:8000/api/materials/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wood",
    "description": "High quality wood"
  }'

# Create a product type
curl -X POST http://localhost:8000/api/product-types/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Table",
    "description": "Furniture table"
  }'

# Create an item (with image processing)
curl -X POST http://localhost:8000/api/items/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "material_id": 1,
    "product_type_id": 1,
    "width": 800,
    "height": 600
  }'
```

## Image Processing Feature

When you create an item:

1. The system crops the original image from position (0, 0) with the specified width and height
2. The cropped section is converted to a PDF
3. A timestamp is added to the PDF
4. The PDF is saved to `storage/pdfs/`
5. The file path is stored in the item record

Example PDF filename: `item_1_2024-01-12_14-30-45.pdf`

## Running Tests

### With Docker

```bash
# Run tests inside the container
docker-compose exec app pytest test_main.py -v
```

### Local Testing (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Make sure MySQL is running on localhost:3306
# Update TEST_DATABASE_URL in test_main.py if needed

# Run tests
pytest test_main.py -v
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout (invalidate token)

### Users
- `POST /api/users/` - Create user (no auth required)
- `GET /api/users/` - List all users (auth required)
- `GET /api/users/{id}` - Get user by ID (auth required)
- `PUT /api/users/{id}` - Update user (auth required)
- `DELETE /api/users/{id}` - Delete user (auth required)

### Materials
- `POST /api/materials/` - Create material
- `GET /api/materials/` - List all materials
- `GET /api/materials/{id}` - Get material by ID
- `PUT /api/materials/{id}` - Update material
- `DELETE /api/materials/{id}` - Delete material

### Product Types
- `POST /api/product-types/` - Create product type
- `GET /api/product-types/` - List all product types
- `GET /api/product-types/{id}` - Get product type by ID
- `PUT /api/product-types/{id}` - Update product type
- `DELETE /api/product-types/{id}` - Delete product type

### Items
- `POST /api/items/` - Create item (triggers image processing)
- `GET /api/items/` - List all items
- `GET /api/items/{id}` - Get item by ID
- `PUT /api/items/{id}` - Update item (regenerates PDF if dimensions change)
- `DELETE /api/items/{id}` - Delete item

All endpoints except user creation and login require JWT authentication.


## Configuration

### Environment Variables

You can modify these in `docker-compose.yml`:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret key (change in production!)

### Database Configuration

Default credentials (change for production):
- Host: localhost
- Port: 3306
- Database: testdb
- User: testuser
- Password: testpass

## Stopping the Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```


## Technologies Used

- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM with async support
- **MySQL** - Relational database
- **JWT** - Token-based authentication
- **Pillow** - Image processing
- **ReportLab** - PDF generation
- **Docker** - Containerization
- **Pytest** - Testing framework

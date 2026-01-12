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
├── main.py                  # FastAPI application entry point
├── database.py              # Database configuration
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic schemas
├── auth.py                  # Authentication utilities
├── image_processor.py       # Image cropping and PDF generation
├── routers/
│   ├── __init__.py
│   ├── auth.py             # Authentication endpoints
│   ├── users.py            # User CRUD endpoints
│   ├── materials.py        # Material CRUD endpoints
│   ├── product_types.py    # Product Type CRUD endpoints
│   └── items.py            # Item CRUD endpoints with image processing
├── static/
│   └── original_image.jpg  # Static image for cropping (you need to add this)
├── output/
│   └── pdfs/               # Generated PDF files
├── test_main.py            # Unit tests
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

## Setup Instructions

### Step 1: Clone and Setup

```bash
# Create project directory
mkdir backend-test-task
cd backend-test-task

# Copy all the provided files into this directory
```

### Step 2: Add Static Image

**IMPORTANT:** You need to add a static image file for the cropping functionality to work.

```bash
# Create static directory
mkdir -p static

# Add your image file (should be large enough to crop from)
# Place your image as: static/original_image.jpg
# Recommended size: at least 1920x1080 pixels or larger
```

You can download a sample image:
```bash
# Example: Download a sample image
wget https://picsum.photos/2000/1500.jpg -O static/original_image.jpg
```

### Step 3: Start with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

The application will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Step 4: Initialize Database (Automatic)

The database tables are created automatically when the application starts.

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
4. The PDF is saved to `output/pdfs/`
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

## Database Schema

### Users Table
- id, username, email, hashed_password, created_at, updated_at

### Token Sessions Table
- id, user_id, token, created_at, expires_at

### Materials Table
- id, name, description, created_at, updated_at

### Product Types Table
- id, name, description, created_at, updated_at

### Items Table
- id, material_id, product_type_id, width, height, pdf_path, created_at, updated_at

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

## Troubleshooting

### Database Connection Issues

```bash
# Check if MySQL is ready
docker-compose logs db

# Restart services
docker-compose restart
```

### Image Processing Issues

Make sure `static/original_image.jpg` exists and is readable:

```bash
ls -la static/original_image.jpg
```

### View Application Logs

```bash
# Follow logs
docker-compose logs -f app

# View database logs
docker-compose logs db
```

## Production Considerations

Before deploying to production:

1. **Change SECRET_KEY** in environment variables
2. **Use strong database passwords**
3. **Add rate limiting**
4. **Implement proper logging**
5. **Add CORS middleware** if needed
6. **Use HTTPS** with proper SSL certificates
7. **Add input validation** and sanitization
8. **Implement proper error handling**
9. **Add database backups**
10. **Monitor application performance**

## Technologies Used

- **FastAPI** - Modern async web framework
- **SQLAlchemy** - ORM with async support
- **MySQL** - Relational database
- **JWT** - Token-based authentication
- **Pillow** - Image processing
- **ReportLab** - PDF generation
- **Docker** - Containerization
- **Pytest** - Testing framework

## License

This is a test task implementation.

## Support

For issues or questions, please check the FastAPI documentation at https://fastapi.tiangolo.com/
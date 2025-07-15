# Background Removal API

A FastAPI-based service for removing backgrounds from images using JWT authentication.

## Features

- JWT-based authentication system
- Background removal from images
- Support for multiple output formats (PNG, JPG, etc.)
- Health check endpoint
- Metrics endpoint for monitoring
- Secure API key authentication

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.8 or higher
- pip (Python package installer)
- curl (for testing API endpoints)

## Installation

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd background-removal-api
```

### Step 2: Create a Virtual Environment

Creating a virtual environment helps isolate your project dependencies from other Python projects on your system.

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
source venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
pip install kornia timm
```

### Step 4: Set Up Environment Variables

Create a `.env` file in your project root directory and configure the following variables:

```env
# API Configuration
API_SECRET_KEY=your-super-secret-key-change-in-production-abc123xyz789
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Server Configuration
HOST=localhost
PORT=8000
DEBUG=True
```

**Important Security Note:** The API key `your-super-secret-key-change-in-production-abc123xyz789` shown in your examples should be changed to a secure, randomly generated key in production environments.

### Step 5: Create Required Directories

The application expects certain directories to exist for input and output files:

```bash
mkdir -p app/images
mkdir -p app/outputs
```

### Step 6: Start the Application

```bash
# Run the FastAPI application
uvicorn main:app --host localhost --port 8000 --reload
```

The `--reload` flag enables automatic reloading when you make code changes during development.

## API Endpoints

### Health Check
- **Endpoint:** `GET /health/`
- **Purpose:** Verify that the API is running correctly
- **Authentication:** Requires API key

### Authentication
- **Endpoint:** `POST /auth/token`
- **Purpose:** Generate JWT access token for API access
- **Parameters:** `user_id` (required)

### Background Removal
- **Endpoint:** `POST /api/remove-background`
- **Purpose:** Remove background from uploaded images
- **Authentication:** Requires JWT Bearer token
- **Parameters:** 
  - `file` (multipart/form-data): Image file to process
  - `output_format` (optional): Output format (PNG, JPG, etc.)

### Metrics
- **Endpoint:** `GET /metrics/`
- **Purpose:** Retrieve API usage metrics and statistics
- **Authentication:** Requires JWT Bearer token

## Testing the API

Follow these steps to test your API endpoints using the provided curl commands:

### Step 1: Test Health Check

This verifies that your API is running and accessible:

```bash
curl -X GET "http://localhost:8000/health/" \
  -H "Authorization: Bearer your-super-secret-key-change-in-production-abc123xyz789"
```

**Expected Response:** A JSON response indicating the API health status.

### Step 2: Generate Access Token

Before using protected endpoints, you need to obtain a JWT token:

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -G -d "user_id=jahid12345"
```

**Expected Response:** A JSON object containing your access token.

**Example Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Step 3: Test Background Removal

Place a test image in the `app/images/` directory (e.g., `profile3.jpg`) and run:

```bash
curl -X POST "http://localhost:8000/api/remove-background" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -F "file=@./app/images/profile3.jpg" \
  -F "output_format=PNG" \
  --output "app/outputs/processed_portrait1.png"
```

**Important:** Replace `YOUR_ACCESS_TOKEN_HERE` with the actual token you received from Step 2.

**Expected Result:** A processed image with the background removed will be saved to `app/outputs/processed_portrait1.png`.

### Step 4: Check Metrics

Monitor your API usage and performance:

```bash
curl -X GET "http://localhost:8000/metrics/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

**Expected Response:** JSON data containing API usage statistics and metrics.

## Understanding the Authentication Flow

The API uses a two-tier authentication system for enhanced security:

1. **API Key Authentication:** Used for initial health checks and token generation
2. **JWT Authentication:** Used for accessing protected endpoints like background removal and metrics

This approach allows you to control access at multiple levels and provides flexibility in managing different types of clients.

## Troubleshooting

### Common Issues and Solutions

**Issue:** "Connection refused" error
**Solution:** Ensure the API server is running on the correct port (8000) and that no firewall is blocking the connection.

**Issue:** "Unauthorized" error
**Solution:** Verify that your API key or JWT token is correct and hasn't expired. JWT tokens have a limited lifespan for security purposes.

**Issue:** "File not found" error
**Solution:** Check that the image file exists in the specified path and that the application has read permissions.

**Issue:** "Invalid token" error
**Solution:** Generate a new JWT token using the `/auth/token` endpoint, as tokens expire after a certain period.


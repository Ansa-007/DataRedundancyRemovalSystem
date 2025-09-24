# Data Redundancy Removal System

A robust system for identifying, classifying, and preventing redundant data entries in cloud databases.

## Features

- **Content Hashing**: Uses BLAKE3 for fast and secure content hashing
- **Duplicate Detection**: Efficiently identifies duplicate content
- **Content Type Detection**: Automatically detects content types
- **RESTful API**: Easy integration with other services
- **Configurable Verification**: Supports manual verification of entries
- **Metadata Support**: Store additional metadata with each entry

## Prerequisites

- Python 3.8+
- SQLite (default) or PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository
2. Navigate to the project directory
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up environment variables (optional, create a `.env` file):
   ```
   DATABASE_URL=sqlite:///./data_redundancy.db
   SECRET_KEY=your-secret-key
   ```

## Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## API Endpoints

### Check for Duplicates

```
POST /api/check
```

Check if content already exists in the system.

**Parameters:**
- `file`: The file to check
- `source`: (Optional) Source identifier
- `metadata`: (Optional) Additional metadata as JSON string

### Submit New Data

```
POST /api/submit
```

Submit new data to the system.

**Parameters:**
- `file`: The file to store
- `source`: (Optional) Source identifier
- `metadata`: (Optional) Additional metadata as JSON string
- `is_verified`: (Optional) Whether the data is verified (default: true)
- `confidence_score`: (Optional) Confidence score 0-100 (default: 100)

### List Entries

```
GET /api/entries
```

List all data entries with optional filtering.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)
- `content_type`: Filter by content type
- `verified`: Filter by verification status

### Get Entry by ID

```
GET /api/entries/{entry_id}
```

Get a specific data entry by its ID.

## Usage Examples

### Checking for Duplicates

```bash
curl -X POST "http://localhost:8000/api/check" \
  -H "accept: application/json" \
  -F "file=@example.txt" \
  -F "source=cli" \
  -F "metadata={\"author\":\"user123\"}"
```

### Submitting New Data

```bash
curl -X POST "http://localhost:8000/api/submit" \
  -H "accept: application/json" \
  -F "file=@example.txt" \
  -F "source=cli" \
  -F "is_verified=true" \
  -F "confidence_score=95"
```

## Configuration

The application can be configured using environment variables:

- `DATABASE_URL`: Database connection URL (default: `sqlite:///./data_redundancy.db`)
- `SECRET_KEY`: Secret key for cryptographic operations
- `LOG_LEVEL`: Logging level (default: `info`)

## Testing

To run the test suite:

```bash
pytest
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.

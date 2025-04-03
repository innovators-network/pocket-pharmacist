# Pocket Pharmacist

An AI-powered chatbot service that helps users easily search and understand medication information in any language.

## Project Structure

```
pocket-pharmacist/
├── corelib/             # Core Business Logic
│   ├── interfaces/      # User Interface Adapters
│   │   └── chatbot.py   # Chatbot Interface
│   ├── orchestration/   # Service Coordination Layer
│   │   └── query_handler.py # Query Processing and Service Orchestration
│   └── services/        # Core Business Services
│       ├── translation_service.py     # AWS Translate Integration
│       ├── intent_recognition_service.py  # AWS Lex Integration
│       └── medical_info_service.py    # OpenFDA API Integration
├── chalicelib/          # AWS Chalice Configuration
│   └── __init__.py      # Chalice Initialization
├── Website/             # Frontend Web Interface
│   ├── index.html      # Main HTML File
│   ├── app.js         # Main Application Logic
│   ├── utils/         # Frontend Utilities
│   │   └── languageUtils.js # Language Utilities
│   └── uiDisplay.js   # UI Display Utilities
├── data/               # Data Files
│   ├── processed/     # Processed Data
│   └── raw/           # Raw Data
├── scripts/            # Utility Scripts
├── tests/              # Test Files
├── .env.example        # Environment Variables Example
├── requirements.txt    # Python Dependencies
├── app.py              # Application Entry Point
└── README.md          # Project Documentation
```

## Tech Stack

- Python 3.8+
- AWS Chalice
- AWS Services (Translate, Lex)
- OpenFDA API
- boto3
- requests

## Installation

1. Clone the repository
```bash
git clone [repository-url]
cd pocket-pharmacist
```

2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Configuration

1. Create `.env` file
```bash
cp .env.example .env
```

2. Set required environment variables in `.env`
```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region

# AWS Lex Configuration
LEX_BOT_ID=your_bot_id
LEX_BOT_ALIAS_ID=your_bot_alias_id

# DynamoDB Configuration
DYNAMODB_TABLE=medical_info
```

## Database Setup

1. Create the DynamoDB table for medical information:
```bash
python scripts/database/create_dynamodb_table.py
```
This script will create a DynamoDB table named `medical_info` (or the value specified in your `DYNAMODB_TABLE` environment variable) with `id` as the primary key.

2. Upload medication data to the DynamoDB table:
```bash
python scripts/database/upload_to_dynamodb.py
```
This script reads data from `data/processed/dynamodb_ready_data.json` and uploads it to the DynamoDB table. The data contains medication information including names, uses, side effects, and substitutes. This data is from Kaggle and converted to json file

## Running the Application

### Local Development

1. Start the backend API server:
```bash
chalice local
```
This will start the API server at http://localhost:8000

2. Start the frontend development server:
```bash
cd Website
python -m http.server 8080
```
This will serve the web interface at http://localhost:8080

3. Access the web interface:
- Open http://127.0.0.1:8080 in your browser
- Start chatting with the Pocket Pharmacist!

### Production Deployment

1. Deploy the application using Chalice
```bash
chalice deploy
```

2. Access the web interface
- Open the provided API Gateway URL in your browser
- Type your question in any language - the system will automatically detect and translate it

## API Usage

### Endpoints

#### 1. Chat Endpoint
- **Endpoint**: `POST /api/chat`
- **Description**: Send a message to the chatbot
- **Examples**:

Using curl:
```bash
curl -X POST https://your-api-gateway-url/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the side effects of Tylenol?", "language": "auto"}'
```

Using JavaScript:
```javascript
fetch('https://your-api-gateway-url/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'What are the side effects of Tylenol?',
    language: 'auto'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

Response Examples:
```json
// Success Response
{
  "status": "success",
  "response": "Side Effects: Nausea, vomiting, loss of appetite, headache, stomach pain, dark urine, clay-colored stools, jaundice (yellowing of skin or eyes).",
  "metadata": {
    "drug_name": "TYLENOL",
    "timestamp": "2024-03-30T12:34:56.789Z",
    "data_source": "OpenFDA"
  }
}

// Error Response
{
  "status": "error",
  "error": "Error message",
  "details": "Detailed error information"
}
```

## Architecture

### Service Layer
The application follows a layered architecture with separation of concerns:

1. **Interface Layer** (`corelib/interfaces/`):
   - Handles interactions with external systems
   - Provides adapters for user interfaces
   - Abstracts application core from delivery mechanisms

2. **Orchestration Layer** (`corelib/orchestration/`):
   - Coordinates between different services
   - Manages the flow of data
   - Handles error cases and session management

3. **Service Layer** (`corelib/services/`):
   - Implements core business logic
   - Integrates with external services (AWS, OpenFDA)
   - Handles data processing and transformation

4. **API Layer** (`app.py`):
   - Built using AWS Chalice
   - Exposes endpoints for client interactions
   - Handles HTTP request/response processing

## Features

1. Multilingual Support
   - Automatic language detection using AWS Translate
   - Seamless translation for both user input and responses
   - No need to specify language - just type in any supported language

2. Intent Recognition
   - User intent recognition via AWS Lex
   - Handles various medication-related queries:
     * Drug side effects
     * Dosage information
     * Drug interactions
     * Warnings and precautions

3. Medication Information
   - OpenFDA API integration
   - Provides comprehensive drug information:
     * Side effects and adverse reactions
     * Dosage and administration
     * Drug interactions
     * Warnings and contraindications

## Development Guide

1. Adding New Features
   - Implement core business logic in `corelib/services/`
   - Add service orchestration in `corelib/orchestration/`
   - Create interface adapters in `corelib/interfaces/`
   - Expose new endpoints in `app.py` if needed

2. Testing
   - Run tests using pytest:
   ```bash
   pytest
   ```
   - Add new tests in the `tests/` directory

## Error Handling

The application implements comprehensive error handling:
- API errors (400, 401, 403, 404, 500)
- Service integration errors
- Input validation errors
- Translation failures
- Intent recognition issues

## Logging

Logs are configured based on the environment:
- Development: Debug level logging
- Production: Info level logging with error tracking
- AWS CloudWatch integration for production monitoring
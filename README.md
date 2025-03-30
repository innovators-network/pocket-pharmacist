# Pocket Pharmacist

An AI-powered chatbot service that helps users easily search and understand medication information in any language.

## Project Structure

```
pocket-pharmacist/
├── chalicelib/           # Main source code
│   ├── interfaces/       # User Interface Layer
│   │   └── chatbot.py   # Chatbot Interface
│   ├── orchestration/   # Service Orchestration Layer
│   │   └── query_handler.py # Query Processing and Service Orchestration
│   └── services/        # Service Implementation Layer
│       ├── translation_service.py     # AWS Translate Integration
│       ├── intent_recognition_service.py  # AWS Lex Integration
│       └── medical_info_service.py    # OpenFDA API Integration
├── Website/             # Frontend web interface
│   ├── index.html      # Main HTML file
│   ├── app.js         # Main application logic
│   ├── utils/         # Frontend utilities
│   │   └── languageUtils.js # Language utilities
│   └── uiDisplay.js   # UI display utilities
├── testing/            # Test files and test data
├── .env.example        # Example environment variables
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
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
```

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
- Open http://localhost:8080/index.html in your browser
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
The application is built using AWS Chalice and follows a layered architecture:

1. **Interface Layer** (`chalicelib/interfaces/`):
   - Handles HTTP requests and responses
   - Manages API endpoints
   - Validates input data

2. **Orchestration Layer** (`chalicelib/orchestration/`):
   - Coordinates between different services
   - Manages the flow of data
   - Handles error cases

3. **Service Layer** (`chalicelib/services/`):
   - Implements core business logic
   - Integrates with external services (AWS, OpenFDA)
   - Handles data processing

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
   - Add new endpoints in `app.py`
   - Implement corresponding handlers in `chalicelib/interfaces/`
   - Add business logic in `chalicelib/services/`

2. Testing
   - Run tests using pytest:
   ```bash
   pytest
   ```
   - Add new tests in the `testing/` directory

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
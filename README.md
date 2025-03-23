# Pocket Pharmacist
A cloud-agnostic medical/drug consultation app with a backend powered by AWS Lex, Chalice, and OpenFDA, and a front-end built with React.js, TypeScript, Bootstrap, and React-Bootstrap.

## Structure
This is a monorepo containing both the backend and front-end:
- **Backend**: The root directory contains the backend code.
- **Frontend** (`web/`): Contains the React.js front-end application.

## Architecture
- **User Interfaces**:
  - **AWS Lex**: Primary user interface, supporting text and voice interactions (e.g., via web, mobile, or voice assistants).
  - **React.js App** (`web/`): Web-based front-end to interact with the backend.
  - Additional frontends (e.g., mobile apps) can be added by creating new Public APIs.
- **Orchestration Layer** (`orchestration/`): Contains Public APIs (`public_apis/`) and Private APIs (`private_apis/`) for business logic.
- **Service Implementations** (`service_implementations/`): Vendor (OpenFDA) and custom service implementations.
- **AWS Adapter** (`app/`): Integrates AWS Lex with the Orchestration Layer using Chalice and a Lex adapter.

## Setup (Backend)
1. Install Python 3.8+ and `pipenv`: `pip install pipenv`
2. Run `./setup.sh` to set up the environment (this will install dependencies using `pipenv`).
3. Activate the virtual environment: `pipenv shell`
4. Add OpenFDA API key to `.chalice/config.json`.
5. Deploy the Lambda function: `chalice deploy`
6. **Configure AWS Lex**:
   - Option 1: Use the AWS Console (see below).
   - Option 2: Run the setup script: `python scripts/setup_lex_bot.py` (update the Lambda ARN in the script first).
7. Test the bot in the Lex console.

## Setup (Frontend)
1. Navigate to the `web/` directory: `cd web`
2. Install Node.js dependencies: `npm install`
3. Start the development server: `npm start`
4. See `web/README.md` for more details.

## AWS Lex Configuration (Manual)
1. In the AWS Console, create a Lex bot named `PocketPharmacistBot`.
2. Define intents (e.g., `GetDrugSideEffects`) with utterances like "What are the side effects of ibuprofen?".
3. Add a slot `drugName` (type: `AMAZON.AlphaNumeric`) to capture the drug name.
4. Set the fulfillment to the Lambda function deployed by Chalice (`LexHandler`).
5. Build and test the bot in the Lex console.

## Testing (Backend)
1. Activate the virtual environment: `pipenv shell`
2. Run tests: `pytest`
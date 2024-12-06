# FHIR API Sample Project

## Features
- Generic FHIR resource validation
- Asynchronous message publishing

## Requirements
- Python 3.13
- FastAPI web framework
- Additional dependencies as listed in `pyproject.toml`

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/joaodaher/fhir-api-fastapi.git
   ```
2. Navigate to the project directory:
   ```sh
   make dependencies
   ```

## Usage
### Running the Application
1. Start the application:
   ```sh
   make run
   ```
   
### Testing
1. Run the tests:
   ```sh
   make test
   ```
   
### Spinning up Docker Containers
1. Build the Docker images and start the containers:
   ```sh
   make docker-build
   ```

### HTTP Requests
- Example requests:
  - Create a Patient resource:
    ```http
    POST http://127.0.0.1:8000/fhir/Patient
    Content-Type: application/json

    {
      "resourceType": "Patient",
      "id": "example",
      "active": true,
      "name": [
        {
          "use": "official",
          "family": "Doe",
          "given": ["John"]
        }
      ]
    }
    ```
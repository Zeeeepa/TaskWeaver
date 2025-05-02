# TaskWeaver UI with Codegen Integration

This module provides a web-based user interface for TaskWeaver with Codegen integration. It allows users to:

1. Add API credentials (GitHub, Codegen, ngrok)
2. Select GitHub repositories
3. Converse with TaskWeaver to create requirements documentation
4. Prompt the Codegen agent to implement the requirements

## Setup

### Prerequisites

- Python 3.8 or higher
- TaskWeaver installed
- Codegen SDK installed
- GitHub account with API token
- Codegen account with API token and organization ID
- ngrok account with API token

### Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure the TaskWeaver and Codegen SDKs are installed:

```bash
pip install codegen
```

## Usage

1. Start the UI server:

```bash
python -m standalone_taskweaver.ui.main
```

2. Open your browser and navigate to `http://localhost:8000`

3. Enter your API credentials:
   - GitHub API token
   - Codegen API token
   - ngrok API token
   - Codegen organization ID

4. Select a GitHub repository from the dropdown

5. Converse with TaskWeaver to create requirements documentation

6. Click "Prompt Codegen Agent" to start the implementation process

## Configuration

You can configure the server host and port by passing command-line arguments:

```bash
python -m standalone_taskweaver.ui.main --host 127.0.0.1 --port 8080
```

## Architecture

The integration consists of the following components:

1. **UI Server**: A FastAPI web server that provides the user interface
2. **Codegen Integration**: A module that integrates TaskWeaver with Codegen
3. **TaskWeaver UI**: A class that manages the UI state and interactions

## API Endpoints

- `GET /`: Main UI page
- `POST /api/credentials`: Set API credentials
- `POST /api/select-repo`: Select a GitHub repository
- `POST /api/converse`: Converse with TaskWeaver
- `POST /api/prompt-codegen`: Prompt Codegen agent with instructions

## License

This project is licensed under the same license as TaskWeaver.


# TaskWeaver

TaskWeaver is a code-first agent framework for seamlessly planning and executing data analytics tasks with Codegen integration.

## Features

- **Code-First Approach**: TaskWeaver prioritizes code generation and execution for data analytics tasks
- **Multiple UI Options**: Web UI, Desktop GUI, and CLI interfaces
- **Codegen Integration**: Seamless integration with Codegen for advanced code generation capabilities
- **Concurrent Task Execution**: Execute multiple tasks concurrently for improved performance
- **Bidirectional Context Sharing**: Share context between TaskWeaver and Codegen
- **Error Handling Framework**: Robust error handling with retry mechanisms
- **Requirements Management**: Parse and manage requirements for complex projects

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/TaskWeaver.git
cd TaskWeaver

# Run the deployment script
# For Linux/macOS:
chmod +x deploy_and_launch.sh
./deploy_and_launch.sh

# For Windows:
deploy_and_launch.bat
```

The deployment script will:
1. Pull the latest changes from the repository
2. Create a virtual environment
3. Install dependencies
4. Set up environment variables
5. Launch TaskWeaver in your preferred mode

### Manual Installation

If you prefer to install manually:

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/TaskWeaver.git
cd TaskWeaver

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Launch TaskWeaver
python main.py --web  # For web UI
# OR
python main.py --gui  # For desktop GUI
# OR
python main.py --cli --project /path/to/project --interactive  # For CLI
```

## Environment Variables

TaskWeaver uses the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `CODEGEN_API_KEY`: Your Codegen API key
- `CODEGEN_ORG_ID`: Your Codegen organization ID
- `GITHUB_TOKEN`: Your GitHub token
- `NGROK_TOKEN`: Your ngrok token (optional, for public access)

You can set these variables in a `.env` file in the project root directory.

## Usage

### Web UI

The web UI provides a user-friendly interface for interacting with TaskWeaver and Codegen.

```bash
python main.py --web --host 0.0.0.0 --port 8000
```

Options:
- `--host`: Host to bind the web server to (default: 0.0.0.0)
- `--port`: Port to bind the web server to (default: 8000)
- `--public`: Make the web UI publicly accessible via ngrok

### Desktop GUI

The desktop GUI provides a native interface for interacting with TaskWeaver.

```bash
python main.py --gui
```

### CLI

The CLI provides a command-line interface for scripting and automation.

```bash
python main.py --cli --project /path/to/project --interactive
```

Options:
- `--project`: Project directory path (required)
- `--interactive`: Run in interactive mode

## Codegen Integration

TaskWeaver integrates with Codegen to provide advanced code generation capabilities. To use Codegen integration:

1. Set your Codegen API key and organization ID in the environment variables
2. Use the web UI or API to interact with Codegen
3. Create tasks, generate code, and analyze code using Codegen

## API Reference

TaskWeaver provides a RESTful API for interacting with the system. The API is available at:

```
http://localhost:8000/api/
```

### Endpoints

- `/api/credentials`: Set API credentials
- `/api/select-repo`: Select a GitHub repository
- `/api/converse`: Converse with TaskWeaver
- `/api/prompt-codegen`: Prompt Codegen agent with instructions
- `/api/codegen/status`: Get the status of the Codegen integration
- `/api/codegen/repositories`: Get list of GitHub repositories
- `/api/codegen/tasks`: Create or list Codegen tasks
- `/api/codegen/generate-code`: Generate code using Codegen
- `/api/codegen/analyze-code`: Analyze code using Codegen
- `/api/codegen/refactor-code`: Refactor code using Codegen
- `/api/codegen/generate-tests`: Generate tests for code using Codegen
- `/api/codegen/context`: Get or update shared context
- `/api/codegen/requirements`: Create or update requirements document
- `/api/codegen/workflow/start`: Start the Codegen workflow
- `/api/codegen/workflow/stop`: Stop the Codegen workflow
- `/api/upload-file`: Upload a file to the server

## Development

### Project Structure

```
TaskWeaver/
├── main.py                      # Main entry point
├── setup.py                     # Package setup
├── deploy_and_launch.sh         # Deployment script for Linux/macOS
├── deploy_and_launch.bat        # Deployment script for Windows
├── requirements.txt             # Dependencies
├── standalone_taskweaver/       # Core TaskWeaver code
│   ├── app/                     # Application code
│   ├── code_interpreter/        # Code interpreter
│   ├── integration/             # Integration modules
│   │   ├── codegen_integration.py  # Codegen integration
│   │   ├── bidirectional_context.py  # Context sharing
│   │   ├── advanced_api.py      # Advanced API
│   │   ├── planner_integration.py  # Planner integration
│   │   └── requirements_manager.py  # Requirements management
│   ├── ui/                      # User interfaces
│   │   ├── server.py            # Web server
│   │   ├── taskweaver_ui.py     # UI class
│   │   ├── templates/           # HTML templates
│   │   └── static/              # Static files
│   └── ...                      # Other modules
└── ...
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.


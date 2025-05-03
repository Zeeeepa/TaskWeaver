# TaskWeaver

TaskWeaver is a code-first agent framework for seamlessly planning and executing data analytics tasks with Codegen integration.

## Features

- **Modular Integration Architecture**: Dedicated `integration` module with clean separation of concerns
- **Bidirectional Context Sharing**: Context sharing between TaskWeaver and Codegen
- **Advanced API Support**: Support for code generation, analysis, refactoring, and testing
- **Requirements Management**: Requirements parser and manager
- **Improved UI**: Enhanced web UI with better styling and functionality
- **Deployment Scripts**: Deployment scripts for both Linux/macOS and Windows

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TaskWeaver.git
   cd TaskWeaver
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

## Usage

### Quick Start

1. Run the deployment script:
   - On Linux/macOS:
     ```bash
     ./deploy_and_launch.sh
     ```
   - On Windows:
     ```bash
     deploy_and_launch.bat
     ```

2. Access the web UI at `http://localhost:8000`

### Configuration

Configuration is stored in `standalone_taskweaver/cli/project/config.yaml`. You can modify this file to change the application settings.

### Environment Variables

The following environment variables are used:

- `OPENAI_API_KEY`: Your OpenAI API key
- `CODEGEN_API_KEY`: Your Codegen API key
- `TASKWEAVER_CONFIG`: Path to the configuration file

## Project Structure

```
TaskWeaver/
├── standalone_taskweaver/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app/
│   │   ├── __init__.py
│   │   └── app.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── codegen_integration.py
│   │   ├── bidirectional_context.py
│   │   └── requirements_manager.py
│   └── cli/
│       ├── __init__.py
│       └── project/
│           └── config.yaml
├── tests/
│   └── test_import.py
├── setup.py
└── taskweaver -> standalone_taskweaver (symlink)
```

## Development

### Running Tests

```bash
python -m pytest
```

### Building Documentation

```bash
cd docs
make html
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- TaskWeaver is built on top of the TaskWeaver framework
- Codegen integration is powered by the Codegen API


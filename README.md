# TaskWeaver

TaskWeaver is a code-first agent framework for seamlessly planning and executing data analytics tasks.

## Features

- **Code-First Approach**: TaskWeaver prioritizes code generation and execution for data analytics tasks
- **Multiple UI Options**: Web UI, Desktop GUI, and CLI interfaces
- **Codegen Integration**: Seamless integration with Codegen for advanced code generation capabilities
- **Concurrent Task Execution**: Execute multiple tasks concurrently for improved performance
- **Bidirectional Context Sharing**: Share context between TaskWeaver and Codegen
- **Error Handling Framework**: Robust error handling with retry mechanisms
- **Requirements Management**: Parse and manage requirements for complex projects

## Installation

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/TaskWeaver.git
cd TaskWeaver

# Install the package
pip install -e .
```

## Usage

### Web UI

```bash
python main.py --web --host 0.0.0.0 --port 8000
```

### Desktop GUI

```bash
python main.py --gui
```

### CLI

```bash
python main.py --cli --project /path/to/project --interactive
```

## Configuration

TaskWeaver can be configured using a configuration file:

```bash
python main.py --config /path/to/config.yaml
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_API_BASE`: (Optional) Custom OpenAI API endpoint
- `OPENAI_MODEL`: (Optional) Custom OpenAI model to use
- `TASKWEAVER_CONFIG_PATH`: (Optional) Path to configuration file

## Development

### Prerequisites

- Python 3.10 or higher
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/TaskWeaver.git
cd TaskWeaver

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.


# TaskWeaver

TaskWeaver is a code-first agent framework for seamlessly planning and executing data analytics tasks.

## Features

- **Code-First Approach**: TaskWeaver uses a code-first approach to data analytics, allowing you to express complex data operations through natural language.
- **Codegen Integration**: Seamlessly integrate with Codegen for enhanced code generation capabilities.
- **Multiple UI Options**: Choose from web UI, desktop GUI, or CLI interfaces based on your needs.
- **Extensible Architecture**: Easily extend TaskWeaver with custom plugins and integrations.

## Installation

```bash
# Clone the repository
git clone https://github.com/microsoft/TaskWeaver.git
cd TaskWeaver

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

TaskWeaver provides multiple interfaces to suit your workflow:

### Web UI

```bash
python main.py --web
```

This will start the web UI on http://localhost:8000 by default.

### Desktop GUI

```bash
python main.py --gui
```

This will launch the PyQt5-based desktop GUI.

### CLI

```bash
python main.py --cli --project /path/to/project
```

This will initialize the CLI with the specified project directory.

## Configuration

TaskWeaver can be configured using environment variables or a configuration file:

```bash
# Set OpenAI API key
export OPENAI_API_KEY=your_api_key_here

# Set custom API base URL (optional)
export OPENAI_API_BASE=https://your-custom-endpoint.com

# Set custom model (optional)
export OPENAI_MODEL=gpt-4
```

You can also specify a configuration file:

```bash
python main.py --config /path/to/config.yaml
```

## Codegen Integration

TaskWeaver includes integration with Codegen for enhanced code generation capabilities. To use this feature:

1. Navigate to the Codegen page in the web UI
2. Initialize the integration with your API credentials
3. Select a repository to work with
4. Create tasks or use the advanced features

## Development

### Project Structure

```
TaskWeaver/
├── main.py                  # Main entry point
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── standalone_taskweaver/   # Core package
│   ├── app/                 # Application core
│   ├── code_interpreter/    # Code interpretation
│   ├── codegen_agent/       # Codegen integration
│   ├── config/              # Configuration
│   ├── ui/                  # User interfaces
│   └── version.py           # Version information
└── project/                 # Project templates
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- This project builds upon the work of the Microsoft TaskWeaver team.
- Special thanks to all contributors who have helped make TaskWeaver better.


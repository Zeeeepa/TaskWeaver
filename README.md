# TaskWeaver

A code-first agent framework for seamlessly planning and executing data analytics tasks.

## Overview

TaskWeaver is a framework designed to help data analysts and scientists automate their workflows using AI agents. It provides a code-first approach to building agents that can understand natural language requests, plan the necessary steps, and execute code to fulfill those requests.

## Features

- **Code-First Approach**: TaskWeaver focuses on generating and executing code to solve data analytics tasks.
- **Natural Language Interface**: Interact with your data using natural language queries.
- **Extensible Plugin System**: Add custom functionality through plugins.
- **Multiple UI Options**: Web UI, GUI, and CLI interfaces available.
- **Rich Data Structure Support**: Work with pandas DataFrames and other complex data structures.

## Installation

```bash
# Clone the repository
git clone https://github.com/microsoft/TaskWeaver.git
cd TaskWeaver

# Install the requirements
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

TaskWeaver can be run in several modes:

### Web UI

```bash
python -m taskweaver --web --port 8000
```

### CLI

```bash
python -m taskweaver --cli --project /path/to/project --interactive
```

### GUI (Requires PyQt5)

```bash
python -m taskweaver --gui
```

## Project Structure

A TaskWeaver project directory typically contains:

```
📦project
 ┣ 📄taskweaver_config.json  # Configuration file
 ┣ 📂plugins                 # Custom plugins
 ┣ 📂logs                    # Log files
 ┗ 📂examples                # Example files for the agent
```

## Configuration

TaskWeaver can be configured using a JSON configuration file. You can specify the path to the configuration file using the `--config` option:

```bash
python -m taskweaver --config /path/to/config.json
```

## Documentation

For more detailed documentation, visit the [TaskWeaver Documentation](https://microsoft.github.io/TaskWeaver/).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

TaskWeaver is developed and maintained by Microsoft Research.


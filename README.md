# Standalone TaskWeaver

This is a standalone implementation of Microsoft's TaskWeaver, a code-first agent framework for seamlessly planning and executing data analytics tasks.

## Overview

TaskWeaver is designed to break down complex tasks into manageable steps, generate appropriate code, and maintain state throughout the execution process. This standalone implementation preserves the core functionality of TaskWeaver while providing a simplified interface.

## Key Components

### 1. App Module
- `TaskWeaverApp`: Main application class
- `SessionManager`: Manages conversation sessions

### 2. Planner Module
- `Planner`: Handles task planning and decomposition
- Implements conversation management and plan generation

### 3. Code Interpreter Module
- `CodeInterpreter`: Executes and verifies code

### 4. Memory Module
- `Memory`: Stores conversation history
- `Conversation`: Manages conversation rounds
- `Post`: Handles message exchange
- `Attachment`: Stores additional data
- `RoundCompressor`: Optimizes conversation history

### 5. Role Module
- `Role`: Base class for different roles
- `RoleRegistry`: Manages available roles
- `PostTranslator`: Handles message translation

### 6. Session Module
- `Session`: Manages individual conversation sessions
- `SessionMetadata`: Stores session information

### 7. LLM Module
- `LLMApi`: Base class for language model integration
- `ChatMessageType`: Defines message structure

### 8. Config Module
- `AppConfigSource`: Manages application configuration
- `ModuleConfig`: Base class for module configurations

## Usage

### Quick Start with the Launcher

TaskWeaver now includes a unified launcher script (`main.py`) that provides a simple way to start the application in different UI modes:

```bash
# Launch the web UI (default)
python main.py

# Launch the web UI with custom host and port
python main.py --web --host 127.0.0.1 --port 8080

# Launch the desktop GUI
python main.py --gui

# Launch the CLI interface with a project directory
python main.py --cli --project /path/to/project

# Launch the CLI in interactive mode
python main.py --cli --project /path/to/project --interactive

# Enable automatic dependency installation
python main.py --auto-install

# Use a custom configuration file
python main.py --config /path/to/config.json

# Enable debug logging
python main.py --debug

# Display version information
python main.py --version
```

### Programmatic Usage

```python
import os
from standalone_taskweaver import AppConfigSource, TaskWeaverApp
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.module.tracing import Tracing

# Create the app config
config = AppConfigSource(
    app_base_path=os.path.dirname(os.path.abspath(__file__)),
)

# Create the logger
logger = TelemetryLogger(
    log_dir=os.path.join(config.app_base_path, "logs"),
)

# Create the tracing
tracing = Tracing()

# Create the app
app = TaskWeaverApp(
    config=config,
    logger=logger,
    tracing=tracing,
)

# Create a session
session = app.create_session(
    session_name="Example Session",
)

# Chat with the session
response = session.chat("Analyze the sales data and create a visualization")
print(response)

# Close the session
session.close()
```

## Features

1. **Interactive Conversation**
   - Full conversation flow implementation
   - Session state and history maintenance
   - Message routing between components

2. **Planning System**
   - Task breakdown into subtasks
   - Dependency management between tasks
   - Plan verification and adjustment

3. **Code Generation and Execution**
   - Python code generation based on plans
   - Code verification and execution
   - Result formatting and presentation

4. **Memory Management**
   - Conversation history storage
   - Attachment and metadata management
   - Compression for optimization

5. **Role System**
   - Support for multiple role types
   - Role registration and management
   - Role-specific configurations

## Requirements

- Python 3.8+
- Dependencies:
  - injector
  - tiktoken
  - yaml
  - typing
  - dataclasses
  - contextlib
  - uuid

## Implementation Notes

This standalone implementation focuses on preserving the core functionality of TaskWeaver while simplifying the interface. It includes all necessary dependencies and components to provide a complete TaskWeaver experience.

The implementation is designed to be modular and extensible, allowing for easy customization and integration with other systems.

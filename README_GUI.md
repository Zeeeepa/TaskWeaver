# TaskWeaver GUI

A graphical user interface for Microsoft's TaskWeaver framework that provides:

1. Chat Interface - Interact with TaskWeaver through a user-friendly chat interface
2. Plan View - Visualize the planning steps and execution flow
3. Local Folder Project Selection - Select and manage different project folders

## Installation

Before using the TaskWeaver GUI, make sure to install all required dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- injector - Dependency injection framework
- tiktoken - Tokenizer for language models
- pyyaml - YAML parser and emitter
- typing-extensions - Backported typing features
- dataclasses - Data class decorator
- uuid - UUID generation
- PyQt5 - GUI framework

## Usage

### Starting the GUI

Run the GUI application:

```bash
python taskweaver_gui.py
```

### Setting Up a Project

1. Click the "Browse" button to select a project folder
2. Click "Initialize TaskWeaver" to set up TaskWeaver with the selected folder
3. Once initialized, you can create and manage sessions

### Working with Sessions

- Click "New Session" to create a new TaskWeaver session
- Select a session from the list to view its history
- Use the chat interface to interact with TaskWeaver
- View the plan in the "Plan" tab
- Browse project files in the "Project Explorer" tab

### Chat Interface

The chat interface allows you to:
- Send messages to TaskWeaver
- View the conversation history
- See TaskWeaver's responses in real-time

### Plan View

The Plan View tab shows:
- The current plan created by TaskWeaver
- Steps and tasks identified for your request
- The execution flow of the plan

### Project Explorer

The Project Explorer allows you to:
- Browse the files in your project folder
- Select files to view or reference in your conversations

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed correctly
2. Check that the project folder contains the necessary files
3. Verify that TaskWeaver is initialized properly

For more detailed information about TaskWeaver, refer to the original documentation.

## License

This GUI is provided under the same license as the original TaskWeaver project.


# TaskWeaver GUI

TaskWeaver GUI provides a graphical user interface for interacting with the TaskWeaver framework. This document explains how to use the GUI interface.

## Features

- **Project Selection**: Select a local folder to analyze with TaskWeaver
- **API Configuration**: Configure API endpoints, keys, and models
- **Session Management**: Create and manage multiple TaskWeaver sessions
- **Interactive Chat**: Communicate with TaskWeaver through a chat interface
- **Plan Visualization**: View TaskWeaver's planning steps

## Getting Started

### Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Launch the GUI:
   ```bash
   python taskweaver_gui.py
   ```

   Or use the launcher:
   ```bash
   python taskweaver_launcher.py
   ```

### Configuration

Before using TaskWeaver, you need to configure the API settings:

1. Click the **Settings** button in the top toolbar
2. Enter your API endpoint (e.g., `https://api.openai.com/v1`)
3. Enter your API key
4. Select the model to use (e.g., `gpt-4`)
5. Click **OK** to save the settings

### Using the GUI

1. **Select a Project Directory**:
   - Click the **Browse** button to select a local folder
   - This folder will be used as the context for TaskWeaver

2. **Initialize TaskWeaver**:
   - Click the **Initialize** button to start TaskWeaver with the selected folder
   - Wait for the initialization to complete

3. **Create a Session**:
   - Click the **New Session** button to create a new TaskWeaver session
   - You can create multiple sessions for different tasks

4. **Chat with TaskWeaver**:
   - Type your message in the input box at the bottom
   - Click **Send** or press Enter to send the message
   - View TaskWeaver's response in the chat history

5. **View the Plan**:
   - Switch to the **Plan View** tab to see TaskWeaver's planning steps
   - This shows how TaskWeaver breaks down your request into subtasks

## CLI Mode

TaskWeaver also supports a command-line interface mode:

```bash
python taskweaver_launcher.py --cli --project /path/to/your/project
```

## Troubleshooting

- **API Connection Issues**: Verify your API endpoint and key in the Settings dialog
- **Initialization Errors**: Check that the selected project directory is valid
- **Session Creation Failures**: Ensure TaskWeaver is properly initialized before creating a session

## License

This project is licensed under the MIT License - see the LICENSE file for details.


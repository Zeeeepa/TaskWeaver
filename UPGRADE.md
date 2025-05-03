# TaskWeaver Upgrade Guide

This document provides instructions for upgrading TaskWeaver to the latest version.

## What's New

### Version Upgrades
- Updated all dependencies to their latest versions
- Added support for newer OpenAI models (gpt-4-turbo, gpt-4o)
- Improved error handling and user experience
- Enhanced CLI interface with command history and more commands
- Improved GUI interface with better feedback and settings management

### New Features
- Model selection dropdown in settings
- Command-line model override with `--model` parameter
- Progress bar for chat responses in GUI
- Session management improvements
- Better error handling and user feedback
- Command history in CLI mode

## Upgrade Instructions

### 1. Update Dependencies

Update your dependencies to the latest versions:

```bash
pip install -r requirements.txt
```

### 2. Command Line Interface Improvements

The CLI now supports more commands and features:

- Command history (saved between sessions)
- Session management commands
- Settings management
- Help system

To see all available commands, type `/help` in the CLI.

### 3. GUI Improvements

The GUI has been enhanced with:

- Progress bar for chat responses
- Better error handling and feedback
- Settings management tab
- Model selection dropdown
- Session management improvements

### 4. Using New Models

You can now easily use newer OpenAI models:

- From the command line: `python main.py --model gpt-4o`
- From the GUI: Select the model in the Settings dialog
- From the CLI: Update settings with `/update_settings`

## Breaking Changes

There are no breaking changes in this upgrade. All existing code and configurations should continue to work as before.

## Troubleshooting

If you encounter any issues after upgrading:

1. Make sure you have the latest dependencies installed
2. Check your API key and endpoint settings
3. Try running with debug logging: `python main.py --debug`
4. If using a custom model, ensure it's available in your OpenAI account

For more help, please open an issue on the GitHub repository.


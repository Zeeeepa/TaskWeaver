# Codegen API Upgrade Documentation

This document outlines the changes made to upgrade the TaskWeaver integration with the Codegen SDK to version 0.55.3.

## Overview of Changes

The Codegen API integration has been upgraded to use the latest SDK version (0.55.3), which includes several improvements and new features. The main components that have been updated are:

1. `codegen.py` - Core agent initialization and task handling
2. `integration.py` - Improved CodegenManager class
3. `advanced_api.py` - Enhanced methods for code generation, analysis, refactoring, and testing

## Key Improvements

### Better API Initialization

The new initialization process is more streamlined and provides better error handling:

```python
# New initialization
self.codegen_agent = Agent(
    token=codegen_token,
    org_id=org_id
)
```

### Improved Task Handling

Task creation and monitoring has been enhanced:

```python
# Create a task
task = self.codegen_integration.run_codegen_task(prompt)

# Monitor task status
while self.codegen_integration.get_task_status(task) not in ["completed", "failed", "cancelled"]:
    task.refresh()
    time.sleep(5)
```

### Enhanced Error Handling

Better error handling has been implemented throughout the codebase:

```python
if self.codegen_integration.get_task_status(task) != "completed":
    self.logger.error(f"Task failed: {task.status}")
    return {"success": False, "error": f"Task failed: {task.status}"}
```

## Backward Compatibility

The upgrade maintains backward compatibility with existing code while adding support for the latest Codegen SDK features. All existing methods continue to work as before, but new methods and features are now available.

## Testing

A new test script (`test_codegen_api.py`) has been added to verify the upgraded API. This script tests all the main functionality of the Codegen integration.

## Usage Examples

### Basic Usage

```python
from standalone_taskweaver.codegen_agent.codegen import CodegenManager

# Initialize the Codegen manager
codegen_manager = CodegenManager(
    codegen_token="your_token_here",
    org_id="your_org_id_here"
)

# Run a simple task
result = codegen_manager.run_task("Generate a function to calculate the factorial of a number")
print(result)
```

### Advanced Usage

```python
from standalone_taskweaver.codegen_agent.advanced_api import CodegenAdvancedAPI

# Initialize the advanced API
advanced_api = CodegenAdvancedAPI(
    codegen_token="your_token_here",
    org_id="your_org_id_here"
)

# Analyze code
analysis_result = advanced_api.analyze_code("def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)")
print(analysis_result)

# Generate tests
test_result = advanced_api.generate_tests("def add(a, b):\n    return a + b")
print(test_result)
```

## Troubleshooting

If you encounter any issues with the upgraded API, please check the following:

1. Ensure you're using the correct token and organization ID
2. Check that your network connection is stable
3. Verify that you have the necessary permissions for the operations you're trying to perform

For more detailed information, please refer to the official Codegen SDK documentation.


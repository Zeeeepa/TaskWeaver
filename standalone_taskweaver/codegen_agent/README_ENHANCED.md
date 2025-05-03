# Enhanced Codegen Agent for TaskWeaver

This directory contains an enhanced implementation of the Codegen agent for TaskWeaver, which supports multithreaded requests to the Codegen API while referencing project requirements and context.

## Features

- **Multithreaded Task Execution**: Execute multiple tasks concurrently using both thread pool and async approaches
- **Context Sharing**: Share context between tasks to ensure consistency
- **Enhanced Prompts**: Include project, requirements, and context information in prompts
- **Task Status Monitoring**: Monitor the status of tasks in real-time
- **Error Handling**: Handle errors with fallback strategies
- **Web UI**: User-friendly web interface for interacting with the system

## Components

### Codegen Agent

The `CodegenAgent` class is the main implementation of the Codegen agent. It provides the following functionality:

- Initialize the Codegen agent with API credentials
- Set project context (name, description, requirements)
- Execute tasks based on requirements
- Monitor task status and results
- Handle errors and provide fallback strategies

### Enhanced UI

The enhanced UI provides a user-friendly interface for interacting with the Codegen agent. It includes the following features:

- Chat interface for creating requirements and plans
- Requirements visualization
- Task status monitoring
- Real-time updates via WebSockets
- Project context management

## Usage

### Running the Enhanced UI

To run the enhanced UI, use the following command:

```bash
python -m standalone_taskweaver.ui.run_enhanced
```

Then open your browser to http://localhost:8000

### API Endpoints

The enhanced UI provides the following API endpoints:

- `/api/credentials`: Set and get API credentials
- `/api/chat/message`: Add a message to the chat
- `/api/chat/history`: Get chat history
- `/api/project/context`: Set project context
- `/api/requirements`: Get requirements
- `/api/tasks/execute`: Execute tasks
- `/api/tasks/status`: Get task execution status
- `/api/tasks/cancel`: Cancel task execution
- `/ws`: WebSocket endpoint for real-time updates

## Workflow

1. User chats with TaskWeaver to create requirements and plan
2. When user is satisfied with the plan, they press Initialize
3. TaskWeaver creates multiple requests to Codegen API
4. Tasks are executed concurrently while respecting dependencies
5. Each task references the project, requirements, and context

## Implementation Details

### Multithreaded Execution

The system supports two approaches for multithreaded execution:

1. **Thread Pool**: Using Python's `concurrent.futures.ThreadPoolExecutor` for parallel execution
2. **Async/Await**: Using Python's `asyncio` for asynchronous execution

### Context Sharing

The `ConcurrentContextManager` class manages context sharing between tasks. It ensures that:

- Each task has access to the relevant context
- Context is updated as tasks are completed
- Dependencies between tasks are respected

### Error Handling

The system includes robust error handling with the following features:

- Retry mechanism for failed tasks
- Fallback strategies for different types of errors
- Detailed error reporting

## Dependencies

- Python 3.8+
- FastAPI
- Uvicorn
- Codegen SDK
- Bootstrap 5 (for UI)
- D3.js (for dependency graph visualization)

## Future Improvements

- Add support for more complex dependency graphs
- Implement more advanced error handling strategies
- Enhance the UI with more visualizations
- Add support for more Codegen API features


# TaskWeaver

<div align="center">
  <img src="https://raw.githubusercontent.com/microsoft/TaskWeaver/main/docs/images/taskweaver-logo.png" alt="TaskWeaver Logo" width="200"/>
</div>

A code-first agent framework for seamlessly planning and executing data analytics tasks with Codegen integration.

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/microsoft/TaskWeaver.git
cd TaskWeaver
python -m venv venv && source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up Codegen API (required for code generation)
export CODEGEN_API_ENDPOINT="your_codegen_api_endpoint"
export CODEGEN_API_KEY="your_codegen_api_key"  # If required

# Launch TaskWeaver
python main.py
```

Visit the [Codegen Documentation](https://codegen.sh/docs) to get your API credentials.

## 🌟 Overview

TaskWeaver is a powerful agent framework designed to break down complex data analytics tasks into manageable steps, plan execution, and maintain state throughout the process. This implementation enhances the original TaskWeaver with Codegen integration, providing a more robust and versatile experience.

## 🔄 Flow Architecture

The TaskWeaver-Codegen integration creates a powerful workflow for data analytics and code generation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          TaskWeaver-Codegen Flow                            │
│                                                                             │
├───────────────┐                                  ┌──────────────┐     │
│                 │                                  │                  │     │
│    User Input   │◄────────────────────────────────►│    Web UI/GUI    │     │
│                 │                                  │                  │     │
└───────────┬─────┘                                  └──────────────┘     │
         │                                                    ▲               │
         ▼                                                    │               │
┌───────────────────┐                                  ┌──────┴───────┐     │
│                 │                                  │                  │     │
│   TaskWeaver    │                                  │   Visualization  │     │
│    Planner      │                                  │                  │     │
│                 │                                  │                  │     │
└───────────┬─────┘                                  └──────────────┘     │
         │                                                    ▲               │
         ▼                                                    │               │
┌───────────────────┐                                  ┌──────┴───────┐     │
│                 │                                  │                  │     │
│    Codegen      │◄────────────────────────────────►│    Execution     │     │
│   Integration   │───────────────────────────────────►│    Environment   │     │
│                 │                                  │                  │     │
└───────────────────┘                                  └──────────────┘     │
                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow Explanation:

1. **User Input**: The process begins with a user query or task description.
2. **TaskWeaver Planner**: Analyzes the input and breaks it down into logical steps.
3. **Codegen Integration**: TaskWeaver is responsible ONLY for planning and sending requests to the Codegen API agent:
   - When TaskWeaver needs code generation, it sends structured requests to Codegen
   - If TaskWeaver encounters errors during execution, it sends requests to Codegen with insights and specific requirements
   - Codegen handles all code generation, optimization, and error resolution
4. **Execution Environment**: Provides the necessary runtime for code execution.
5. **Results Visualization**: Formats and presents the results to the user.
6. **Web UI/GUI**: Provides an interactive interface for the entire process.

## 📦 Installation

### Prerequisites
- Python 3.8+
- Git
- Codegen API access (sign up at [codegen.sh](https://codegen.sh))

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/microsoft/TaskWeaver.git
cd TaskWeaver

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for Codegen integration
pip install requests PyQt5
```

### Configuration

Create a configuration file `config.json` in the project root:

```json
{
  "codegen": {
    "api_endpoint": "https://api.codegen.sh/v2/generate",
    "api_key": "your_codegen_api_key",
    "timeout": 30
  },
  "taskweaver": {
    "model": "gpt-4",
    "memory_limit": 1000,
    "log_level": "info"
  }
}
```

Alternatively, set environment variables:

```bash
# Required for Codegen integration
export CODEGEN_API_ENDPOINT="https://api.codegen.sh/v2/generate"
export CODEGEN_API_KEY="your_codegen_api_key"

# Optional TaskWeaver configuration
export TASKWEAVER_MODEL="gpt-4"
export TASKWEAVER_LOG_LEVEL="debug"
```

### Version Compatibility

TaskWeaver-Codegen integration is compatible with:
- TaskWeaver v1.0.0 or later
- Codegen API v2.0.0 or later

For the latest compatibility information, please refer to the [official documentation](https://github.com/microsoft/TaskWeaver/tree/main/docs).

## 🔧 Deployment Setup Guide

### Local Development Deployment

For local development and testing:

1. **Clone and Set Up Environment**:
   ```bash
   git clone https://github.com/microsoft/TaskWeaver.git
   cd TaskWeaver
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   ```bash
   # Create a .env file in the project root
   echo "CODEGEN_API_ENDPOINT=https://api.codegen.sh/v2/generate" > .env
   echo "CODEGEN_API_KEY=your_codegen_api_key" >> .env
   echo "TASKWEAVER_MODEL=gpt-4" >> .env
   echo "TASKWEAVER_LOG_LEVEL=info" >> .env
   ```

3. **Run Development Server**:
   ```bash
   python main.py --web --host 127.0.0.1 --port 8080 --debug
   ```

### Production Deployment

For production environments:

1. **System Requirements**:
   - 4+ CPU cores
   - 8+ GB RAM
   - 20+ GB disk space
   - Python 3.8+ installed

2. **Setup with Docker**:
   ```bash
   # Build the Docker image
   docker build -t taskweaver:latest .

   # Run the container
   docker run -d \
     -p 8080:8080 \
     -e CODEGEN_API_ENDPOINT="https://api.codegen.sh/v2/generate" \
     -e CODEGEN_API_KEY="your_codegen_api_key" \
     -e TASKWEAVER_MODEL="gpt-4" \
     -e TASKWEAVER_LOG_LEVEL="info" \
     --name taskweaver-app \
     taskweaver:latest
   ```

3. **Setup with Systemd (Linux)**:
   Create a systemd service file at `/etc/systemd/system/taskweaver.service`:
   ```
   [Unit]
   Description=TaskWeaver Service
   After=network.target

   [Service]
   User=taskweaver
   WorkingDirectory=/opt/taskweaver
   ExecStart=/opt/taskweaver/venv/bin/python /opt/taskweaver/main.py --web --host 0.0.0.0 --port 8080
   Restart=always
   Environment=CODEGEN_API_ENDPOINT=https://api.codegen.sh/v2/generate
   Environment=CODEGEN_API_KEY=your_codegen_api_key
   Environment=TASKWEAVER_MODEL=gpt-4
   Environment=TASKWEAVER_LOG_LEVEL=info

   [Install]
   WantedBy=multi-user.target
   ```

   Then enable and start the service:
   ```bash
   sudo systemctl enable taskweaver
   sudo systemctl start taskweaver
   ```

4. **Nginx Configuration (Optional)**:
   For production deployments, it's recommended to use Nginx as a reverse proxy:
   ```
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

5. **Monitoring and Logging**:
   - Set up log rotation with logrotate
   - Configure monitoring with Prometheus and Grafana
   - Set up alerts for service disruptions

### Scaling Considerations

For high-traffic deployments:

1. **Horizontal Scaling**:
   - Deploy multiple instances behind a load balancer
   - Use Redis or another distributed cache for session management

2. **Database Integration**:
   - For persistent storage, configure a PostgreSQL database
   - Update the configuration to use the database for task history and results

3. **Memory Management**:
   - Adjust the `memory_limit` setting based on your server's capabilities
   - Monitor memory usage and adjust as needed

4. **Security Considerations**:
   - Enable HTTPS with Let's Encrypt
   - Implement authentication for API access
   - Regularly update dependencies and apply security patches

## 📋 Input Requirements

### TaskWeaver Input Requirements

1. **Task Description**:
   - Natural language description of the data analytics task
   - Specific goals or questions to be answered
   - Any constraints or preferences for the analysis

2. **Data Sources**:
   - File paths or URLs to data sources
   - Database connection parameters (if applicable)
   - API credentials (if accessing external data)

3. **Configuration Parameters**:
   - Model selection (e.g., OpenAI model)
   - API keys and endpoints
   - Memory and processing constraints

4. **Optional Parameters**:
   - Output format preferences
   - Visualization types
   - Execution timeout limits

### Codegen Input Requirements

1. **Code Context**:
   - Existing codebase or repository information
   - Language and framework specifications
   - Coding standards and conventions

2. **Enhancement Requests**:
   - Specific code improvements needed
   - Performance optimization targets
   - Error handling requirements

3. **Integration Parameters**:
   - API endpoints for Codegen services
   - Authentication credentials
   - Response format preferences

## 🔌 Interaction Capabilities

### TaskWeaver Capabilities

1. **Task Planning**:
   - Breaking down complex tasks into subtasks
   - Identifying dependencies between tasks
   - Creating execution plans with proper sequencing

2. **Request Formulation**:
   - Creating structured requests for Codegen
   - Specifying requirements and constraints
   - Providing context for code generation

3. **Execution Management**:
   - Running code in a controlled environment
   - Handling errors and exceptions
   - Managing computational resources

4. **Memory and State**:
   - Maintaining conversation history
   - Tracking variable states across execution steps
   - Storing intermediate results

### Codegen Capabilities

1. **Code Generation**:
   - Creating Python code for data analysis
   - Generating data visualization scripts
   - Implementing statistical models and algorithms

2. **Code Enhancement**:
   - Optimizing generated code for performance
   - Implementing best practices and patterns
   - Adding robust error handling

3. **Library Selection**:
   - Recommending appropriate libraries for tasks
   - Ensuring compatibility between dependencies
   - Implementing efficient import strategies

4. **Code Review**:
   - Analyzing code for potential issues
   - Suggesting improvements and alternatives
   - Ensuring code quality and readability

### Combined System Capabilities

1. **End-to-End Analytics Workflow**:
   - From natural language to executable code
   - Complete data analysis pipeline creation
   - Results visualization and interpretation

2. **Interactive Development**:
   - Real-time code generation and execution
   - Iterative refinement based on feedback
   - Conversation-driven development

3. **Multi-Modal Interfaces**:
   - Web UI for browser-based access
   - Desktop GUI for local development
   - CLI for automation and scripting

4. **Extensibility**:
   - Plugin system for custom components
   - API access for external integration
   - Customizable templates and workflows

## 🚀 Usage Instructions

### Web UI (Default)

The web interface provides the most user-friendly experience with full Codegen integration:

```bash
# Launch with default settings
python main.py

# Launch with custom host and port
python main.py --web --host 127.0.0.1 --port 8080
```

### Desktop GUI

The desktop application offers a native experience:

```bash
# Launch the desktop GUI
python main.py --gui
```

### Command Line Interface (CLI)

For automation and scripting:

```bash
# Launch with a project directory
python main.py --cli --project /path/to/project

# Launch in interactive mode
python main.py --cli --project /path/to/project --interactive
```

### Common Options

```bash
# Enable automatic dependency installation
python main.py --auto-install

# Use a custom configuration file
python main.py --config /path/to/config.json

# Enable debug logging
python main.py --debug

# Display version information
python main.py --version
```

## 📊 Example Workflows

### Data Analysis Workflow

```
User: "Analyze the sales data from 'sales.csv' and create a visualization showing monthly trends"

TaskWeaver:
1. Breaks down the task into: data loading, cleaning, analysis, and visualization
2. Sends request to Codegen API for code generation
3. Codegen generates optimized code for each step
4. TaskWeaver executes the code
5. Returns visualizations and insights
```

### Machine Learning Workflow

```
User: "Build a prediction model for customer churn using 'customer_data.csv'"

TaskWeaver:
1. Plans the ML pipeline: preprocessing, feature engineering, model selection, training, evaluation
2. Sends structured request to Codegen API
3. Codegen generates code with best practices and optimizations
4. TaskWeaver executes the pipeline
5. Returns model performance metrics and predictions
```

### Error Handling Workflow

```
User: "Combine data from 'users.json' and 'purchases.csv' and analyze purchase patterns"

TaskWeaver:
1. Plans the integration approach: data loading, schema alignment, joining, analysis
2. Sends request to Codegen API
3. Executes the generated code
4. Encounters an error in the schema alignment
5. Sends error details and context to Codegen API
6. Codegen provides corrected code with proper error handling
7. TaskWeaver executes the fixed code
8. Returns insights about purchase patterns
```

## 💻 Advanced Usage

### Programmatic Integration

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

### Codegen API Integration

```python
import requests
import json
import os

def send_request_to_codegen(task_description, code_context=None, error_details=None):
    """
    Send a request to Codegen API for code generation or error resolution
    
    Args:
        task_description: Description of the task to perform
        code_context: Optional context about existing code
        error_details: Optional details about errors encountered
        
    Returns:
        Generated code from Codegen API
    """
    # Get API endpoint from environment variable or configuration
    # Replace this with your actual Codegen API endpoint from your configuration
    api_endpoint = os.getenv("CODEGEN_API_ENDPOINT", "https://api.codegen.example/generate")
    
    # Check if the endpoint is still the default placeholder
    if "codegen.example" in api_endpoint:
        print("WARNING: You are using a placeholder API endpoint. Please set the CODEGEN_API_ENDPOINT environment variable.")
    
    payload = {
        "task": task_description,
        "language": "python",
    }
    
    if code_context:
        payload["context"] = code_context
        
    if error_details:
        payload["error"] = error_details
        payload["request_type"] = "error_resolution"
    
    # Add authentication if required by your Codegen API instance
    headers = {
        "Content-Type": "application/json",
        # Uncomment and set your API key if required
        # "Authorization": f"Bearer {os.getenv('CODEGEN_API_KEY')}"
    }
    
    response = requests.post(
        api_endpoint,
        headers=headers,
        data=json.dumps(payload)
    )
    
    if response.status_code == 200:
        return response.json()["generated_code"]
    else:
        raise Exception(f"Codegen API error: {response.text}")
```

## 🛠️ Requirements

- Python 3.8+
- Dependencies:
  - injector
  - tiktoken
  - yaml
  - typing
  - dataclasses
  - contextlib
  - uuid
  - PyQt5 (for GUI mode)
  - requests (for Codegen integration)

## ❓ Troubleshooting

### Common Issues

1. **API Connection Errors**:
   - Ensure your Codegen API credentials are correctly configured
   - Check network connectivity to the Codegen API endpoint
   - Verify that the API endpoint URL is correct in your configuration

2. **Code Execution Failures**:
   - Check that all required dependencies are installed
   - Ensure input data files exist and are accessible
   - Review execution environment permissions

3. **Integration Issues**:
   - Verify TaskWeaver and Codegen version compatibility
   - Check that request formats match the expected API schema
   - Ensure proper error handling in integration code

### Debugging Tips

- Enable debug logging with the `--debug` flag for detailed information
- Check the logs directory for error messages and stack traces
- Use the CLI mode with `--interactive` flag for step-by-step debugging

### Getting Help

If you encounter issues not covered here, please:
- Check the [GitHub Issues](https://github.com/microsoft/TaskWeaver/issues) for similar problems
- Join the [TaskWeaver Community](https://github.com/microsoft/TaskWeaver/discussions) for support
- Refer to the [Codegen Documentation](https://codegen.sh/docs) for API-specific questions

## 📚 Additional Resources

- [TaskWeaver Documentation](https://github.com/microsoft/TaskWeaver/tree/main/docs)
- [Codegen Documentation](https://codegen.sh/docs)
- [API Reference](https://github.com/microsoft/TaskWeaver/tree/main/docs/api)
- [Examples Repository](https://github.com/microsoft/TaskWeaver/tree/main/examples)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

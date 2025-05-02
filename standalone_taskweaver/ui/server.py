"""
Web server for TaskWeaver UI
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-ui")

# Create FastAPI app
app = FastAPI(title="TaskWeaver UI")

# Get the directory of this file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Set up templates
templates_dir = os.path.join(current_dir, "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Set up static files
static_dir = os.path.join(current_dir, "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Store API credentials
api_credentials = {
    "github_token": "",
    "codegen_token": "",
    "ngrok_token": "",
    "codegen_org_id": ""
}

# Store GitHub repositories
github_repos = []

class TaskWeaverUI:
    """
    TaskWeaver UI class
    """
    
    @inject
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.codegen_integration = CodegenIntegration(app, config, logger)
        
    def initialize_integration(self):
        """
        Initialize Codegen integration with API credentials
        """
        if not all([
            api_credentials["github_token"],
            api_credentials["codegen_token"],
            api_credentials["ngrok_token"],
            api_credentials["codegen_org_id"]
        ]):
            return False
            
        try:
            # Initialize Codegen integration
            success = self.codegen_integration.initialize(
                github_token=api_credentials["github_token"],
                codegen_token=api_credentials["codegen_token"],
                ngrok_token=api_credentials["ngrok_token"],
                codegen_org_id=api_credentials["codegen_org_id"]
            )
            
            return success
        except Exception as e:
            logger.error(f"Error initializing Codegen integration: {str(e)}")
            return False
            
    def get_github_repos(self) -> List[str]:
        """
        Get list of GitHub repositories
        """
        return self.codegen_integration.get_repositories()

# Create TaskWeaverUI instance
taskweaver_ui = None

@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    """
    global taskweaver_ui
    # In a real implementation, you would inject the TaskWeaverApp instance
    # For now, we'll create a placeholder
    taskweaver_ui = TaskWeaverUI(None, None, None)

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Get index page
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "api_credentials": api_credentials,
            "github_repos": github_repos
        }
    )

@app.post("/api/credentials")
async def set_credentials(
    github_token: str = Form(...),
    codegen_token: str = Form(...),
    ngrok_token: str = Form(...),
    codegen_org_id: str = Form(...)
):
    """
    Set API credentials
    """
    global api_credentials
    
    api_credentials = {
        "github_token": github_token,
        "codegen_token": codegen_token,
        "ngrok_token": ngrok_token,
        "codegen_org_id": codegen_org_id
    }
    
    # Initialize integration
    if taskweaver_ui:
        success = taskweaver_ui.initialize_integration()
        if success:
            # Get GitHub repositories
            global github_repos
            github_repos = taskweaver_ui.get_github_repos()
            
            return JSONResponse(content={"status": "success", "message": "Credentials set successfully", "repos": github_repos})
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to initialize Codegen integration with provided credentials"})
    
    return JSONResponse(content={"status": "error", "message": "TaskWeaverUI not initialized"})

@app.post("/api/select-repo")
async def select_repo(repo_name: str = Form(...)):
    """
    Select a GitHub repository
    """
    if not taskweaver_ui or not taskweaver_ui.codegen_integration:
        return JSONResponse(content={"status": "error", "message": "Codegen integration not initialized"})
        
    try:
        # Set the repository
        success = taskweaver_ui.codegen_integration.set_repository(repo_name)
        
        if success:
            return JSONResponse(content={"status": "success", "message": f"Repository {repo_name} selected"})
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to set repository"})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"Error selecting repository: {str(e)}"})

@app.post("/api/converse")
async def converse(message: str = Form(...)):
    """
    Converse with TaskWeaver
    """
    if not taskweaver_ui:
        return JSONResponse(content={"status": "error", "message": "TaskWeaverUI not initialized"})
        
    try:
        # In a real implementation, you would use the TaskWeaver API to converse
        # For now, we'll just return a placeholder response
        
        # Generate requirements documentation based on the conversation
        requirements = f"# Requirements\n\n## Feature Request\n\n{message}\n\n## Implementation Plan\n\n1. Analyze the requirements\n2. Design the solution\n3. Implement the solution\n4. Test the implementation\n5. Deploy the solution"
        
        return JSONResponse(content={"status": "success", "message": "Conversation processed", "requirements": requirements})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"Error processing conversation: {str(e)}"})

@app.post("/api/prompt-codegen")
async def prompt_codegen(requirements: str = Form(...)):
    """
    Prompt Codegen agent with instructions
    """
    if not taskweaver_ui or not taskweaver_ui.codegen_integration:
        return JSONResponse(content={"status": "error", "message": "Codegen integration not initialized"})
        
    try:
        # Create a Codegen task
        task_id = taskweaver_ui.codegen_integration.create_codegen_task(requirements)
        
        if task_id:
            return JSONResponse(content={"status": "success", "message": "Codegen task created", "task_id": task_id})
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to create Codegen task"})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": f"Error creating Codegen task: {str(e)}"})

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the web server
    """
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()

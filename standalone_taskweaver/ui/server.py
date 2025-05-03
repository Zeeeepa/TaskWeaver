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

# Store active tasks
active_tasks = {}

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
            
    def get_github_repos(self) -> List[Dict[str, Any]]:
        """
        Get list of GitHub repositories
        """
        if not self.codegen_integration.is_initialized:
            if not self.initialize_integration():
                return []
                
        return self.codegen_integration.get_repositories()
        
    def set_repository(self, repo_name: str) -> bool:
        """
        Set the active GitHub repository
        """
        if not self.codegen_integration.is_initialized:
            if not self.initialize_integration():
                return False
                
        return self.codegen_integration.set_repository(repo_name)
        
    def create_codegen_task(self, prompt: str, repo_name: Optional[str] = None) -> Optional[str]:
        """
        Create a Codegen task
        """
        if not self.codegen_integration.is_initialized:
            if not self.initialize_integration():
                return None
                
        return self.codegen_integration.create_codegen_task(prompt, repo_name)
        
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a Codegen task
        """
        if not self.codegen_integration.is_initialized:
            if not self.initialize_integration():
                return None
                
        return self.codegen_integration.get_task_status(task_id)
        
    def create_requirements_document(self, requirements: str) -> Dict[str, Any]:
        """
        Create or update a REQUIREMENTS.md file in the repository
        """
        if not self.codegen_integration.is_initialized:
            if not self.initialize_integration():
                return {"success": False, "error": "Codegen integration not initialized"}
                
        success, error = self.codegen_integration.create_requirements_document(requirements)
        return {"success": success, "error": error}
        
    def start_workflow(self) -> bool:
        """
        Start the Codegen workflow
        """
        if not self.codegen_integration.is_initialized:
            if not self.initialize_integration():
                return False
                
        return self.codegen_integration.start_workflow()
        
    def stop_workflow(self) -> bool:
        """
        Stop the Codegen workflow
        """
        if not self.codegen_integration.is_initialized:
            if not self.initialize_integration():
                return False
                
        return self.codegen_integration.stop_workflow()
        
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get the status of the Codegen integration
        """
        if not self.codegen_integration.is_initialized:
            return {
                "initialized": False,
                "github_connected": False,
                "codegen_connected": False,
                "ngrok_connected": False,
                "workflow_manager": False,
                "repository": None
            }
            
        return self.codegen_integration.get_status()

# Create TaskWeaverUI instance
ui = TaskWeaverUI(None, None, None)

# API routes
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Get the index page
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/set_credentials")
async def set_credentials(
    github_token: str = Form(...),
    codegen_token: str = Form(...),
    ngrok_token: str = Form(...),
    codegen_org_id: str = Form(...)
):
    """
    Set API credentials
    """
    api_credentials["github_token"] = github_token
    api_credentials["codegen_token"] = codegen_token
    api_credentials["ngrok_token"] = ngrok_token
    api_credentials["codegen_org_id"] = codegen_org_id
    
    # Initialize Codegen integration
    success = ui.initialize_integration()
    
    if success:
        # Get GitHub repositories
        global github_repos
        github_repos = ui.get_github_repos()
        
    return {"success": success}

@app.get("/api/get_repos")
async def get_repos():
    """
    Get list of GitHub repositories
    """
    repos = ui.get_github_repos()
    return {"repos": repos}

@app.post("/api/set_repository")
async def set_repository(repo_name: str = Form(...)):
    """
    Set the active GitHub repository
    """
    success = ui.set_repository(repo_name)
    return {"success": success}

@app.post("/api/create_task")
async def create_task(prompt: str = Form(...), repo_name: Optional[str] = Form(None)):
    """
    Create a Codegen task
    """
    task_id = ui.create_codegen_task(prompt, repo_name)
    
    if task_id:
        # Store task in active tasks
        active_tasks[task_id] = {
            "id": task_id,
            "prompt": prompt,
            "repo_name": repo_name,
            "status": "created",
            "created_at": None,
            "updated_at": None,
            "completed": False,
            "result": None
        }
        
        return {"success": True, "task_id": task_id}
    else:
        return {"success": False, "error": "Failed to create task"}

@app.get("/api/get_task_status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a Codegen task
    """
    status = ui.get_task_status(task_id)
    
    if status:
        # Update active task
        if task_id in active_tasks:
            active_tasks[task_id].update(status)
            
        return {"success": True, "status": status}
    else:
        return {"success": False, "error": "Failed to get task status"}

@app.get("/api/get_active_tasks")
async def get_active_tasks():
    """
    Get all active tasks
    """
    return {"success": True, "tasks": active_tasks}

@app.post("/api/create_requirements")
async def create_requirements(requirements: str = Form(...)):
    """
    Create or update a REQUIREMENTS.md file in the repository
    """
    result = ui.create_requirements_document(requirements)
    return result

@app.post("/api/start_workflow")
async def start_workflow():
    """
    Start the Codegen workflow
    """
    success = ui.start_workflow()
    return {"success": success}

@app.post("/api/stop_workflow")
async def stop_workflow():
    """
    Stop the Codegen workflow
    """
    success = ui.stop_workflow()
    return {"success": success}

@app.get("/api/get_integration_status")
async def get_integration_status():
    """
    Get the status of the Codegen integration
    """
    status = ui.get_integration_status()
    return {"success": True, "status": status}

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the server
    """
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()

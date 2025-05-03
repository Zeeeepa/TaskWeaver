"""
Web server for TaskWeaver UI
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, Depends, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.integration.codegen_integration import CodegenIntegration
from standalone_taskweaver.integration.bidirectional_context import BidirectionalContext
from standalone_taskweaver.integration.advanced_api import AdvancedAPI
from standalone_taskweaver.integration.planner_integration import PlannerIntegration
from standalone_taskweaver.integration.requirements_manager import RequirementsManager
from standalone_taskweaver.ui.taskweaver_ui import TaskWeaverUI

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

# Store OpenAI settings
openai_settings = {
    "api_key": "",
    "api_base": "",
    "model": ""
}

# Store GitHub repositories
github_repos = []

# Store active tasks
active_tasks = {}

# Create TaskWeaverUI instance
ui = None

# API Models
class InitializeRequest(BaseModel):
    github_token: str
    codegen_token: str
    ngrok_token: str
    codegen_org_id: str

class SetRepositoryRequest(BaseModel):
    repo_name: str

class CreateTaskRequest(BaseModel):
    prompt: str
    repo_name: Optional[str] = None

class GenerateCodeRequest(BaseModel):
    prompt: str
    language: str

class AnalyzeCodeRequest(BaseModel):
    code: str
    language: str

class RefactorCodeRequest(BaseModel):
    code: str
    language: str
    instructions: str

class GenerateTestsRequest(BaseModel):
    code: str
    language: str

class ContextUpdateRequest(BaseModel):
    context: Dict[str, Any]

class IssueRequest(BaseModel):
    issue_number: int

class PrRequest(BaseModel):
    pr_number: int

class FileRequest(BaseModel):
    file_path: str

class RequirementsRequest(BaseModel):
    requirements: str

class OpenAISettingsRequest(BaseModel):
    openai_api_key: str
    openai_api_base: Optional[str] = None
    openai_model: Optional[str] = None

# Initialize UI
def get_ui():
    global ui
    if ui is None:
        ui = TaskWeaverUI(None, None, None)
    return ui

# API routes
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Get the index page
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/codegen", response_class=HTMLResponse)
async def get_codegen(request: Request):
    """
    Get the Codegen page
    """
    return templates.TemplateResponse("codegen.html", {"request": request})

@app.get("/api/codegen/status")
async def get_codegen_status():
    """
    Get the status of the Codegen integration
    """
    ui = get_ui()
    status = ui.get_integration_status()
    return status

@app.post("/api/openai-settings")
async def set_openai_settings(
    openai_api_key: str = Form(...),
    openai_api_base: str = Form(None),
    openai_model: str = Form(None)
):
    """
    Set OpenAI API settings
    """
    ui = get_ui()
    
    # Update OpenAI settings
    openai_settings["api_key"] = openai_api_key
    if openai_api_base:
        openai_settings["api_base"] = openai_api_base
    if openai_model:
        openai_settings["model"] = openai_model
    
    # Set environment variables
    os.environ["OPENAI_API_KEY"] = openai_api_key
    if openai_api_base:
        os.environ["OPENAI_API_BASE"] = openai_api_base
    if openai_model:
        os.environ["OPENAI_MODEL"] = openai_model
    
    # Update UI settings
    ui.set_openai_settings(
        api_key=openai_api_key,
        api_base=openai_api_base,
        model=openai_model
    )
    
    return {"status": "success", "message": "OpenAI settings updated successfully"}

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
    ui = get_ui()
    
    # Update API credentials
    api_credentials["github_token"] = github_token
    api_credentials["codegen_token"] = codegen_token
    api_credentials["ngrok_token"] = ngrok_token
    api_credentials["codegen_org_id"] = codegen_org_id
    
    # Initialize Codegen integration
    success = ui.initialize_integration(
        github_token=github_token,
        codegen_token=codegen_token,
        ngrok_token=ngrok_token,
        codegen_org_id=codegen_org_id
    )
    
    if success:
        # Get GitHub repositories
        repos = ui.get_github_repos()
        return {"status": "success", "repos": repos}
    else:
        return {"status": "error", "message": "Failed to initialize Codegen integration"}

@app.post("/api/select-repo")
async def select_repo(repo_name: str = Form(...)):
    """
    Select a GitHub repository
    """
    ui = get_ui()
    success = ui.set_repository(repo_name)
    
    if success:
        return {"status": "success"}
    else:
        return {"status": "error", "message": "Failed to select repository"}

@app.post("/api/converse")
async def converse(message: str = Form(...)):
    """
    Converse with TaskWeaver
    """
    ui = get_ui()
    
    # Process the message and update requirements
    # This is a placeholder for the actual conversation logic
    requirements = f"# Requirements\n\n- Implement {message}\n  This is a placeholder for the actual requirements.\n"
    
    return {"status": "success", "requirements": requirements}

@app.post("/api/prompt-codegen")
async def prompt_codegen(requirements: str = Form(...)):
    """
    Prompt Codegen agent with requirements
    """
    ui = get_ui()
    
    # Create a Codegen task with the requirements
    result = ui.create_codegen_task(requirements)
    
    if result.get("success", False):
        return {"status": "success", "task_id": result.get("task_id")}
    else:
        return {"status": "error", "message": result.get("error", "Failed to create Codegen task")}

@app.post("/api/codegen/initialize")
async def initialize_codegen(request: InitializeRequest):
    """
    Initialize Codegen integration
    """
    ui = get_ui()
    
    # Update API credentials
    api_credentials["github_token"] = request.github_token
    api_credentials["codegen_token"] = request.codegen_token
    api_credentials["ngrok_token"] = request.ngrok_token
    api_credentials["codegen_org_id"] = request.codegen_org_id
    
    # Initialize Codegen integration
    success = ui.initialize_integration(
        github_token=request.github_token,
        codegen_token=request.codegen_token,
        ngrok_token=request.ngrok_token,
        codegen_org_id=request.codegen_org_id
    )
    
    if success:
        # Get GitHub repositories
        global github_repos
        github_repos = ui.get_github_repos()
        
    return {"success": success}

@app.get("/api/codegen/repositories")
async def get_repositories():
    """
    Get list of GitHub repositories
    """
    ui = get_ui()
    repos = ui.get_github_repos()
    
    # Get active repository
    status = ui.get_integration_status()
    active_repo = status.get("repository", None)
    
    return {"success": True, "repositories": repos, "active_repository": active_repo}

@app.post("/api/codegen/repository")
async def set_repository(request: SetRepositoryRequest):
    """
    Set the active GitHub repository
    """
    ui = get_ui()
    success = ui.set_repository(request.repo_name)
    return {"success": success}

@app.post("/api/codegen/tasks")
async def create_task(request: CreateTaskRequest):
    """
    Create a Codegen task
    """
    ui = get_ui()
    result = ui.create_codegen_task(request.prompt, request.repo_name)
    
    if result.get("success", False):
        # Store task in active tasks
        task_id = result.get("task_id")
        active_tasks[task_id] = {
            "id": task_id,
            "prompt": request.prompt,
            "repo_name": request.repo_name,
            "status": "created",
            "created_at": None,
            "updated_at": None,
            "completed": False,
            "result": None
        }
    
    return result

@app.get("/api/codegen/tasks")
async def get_tasks():
    """
    Get all tasks
    """
    ui = get_ui()
    result = ui.list_tasks()
    
    # If no tasks from the API, use the active tasks
    if not result.get("success", False) or not result.get("tasks"):
        tasks = []
        for task_id, task in active_tasks.items():
            # Get latest status
            status = ui.get_task_status(task_id)
            if status.get("success", False):
                task.update(status.get("task", {}))
            tasks.append(task)
        
        return {"success": True, "tasks": tasks}
    
    return result

@app.get("/api/codegen/tasks/{task_id}")
async def get_task(task_id: str):
    """
    Get a specific task
    """
    ui = get_ui()
    result = ui.get_task_status(task_id)
    
    if result.get("success", False):
        # Update active task
        if task_id in active_tasks:
            active_tasks[task_id].update(result.get("task", {}))
    
    return result

@app.post("/api/codegen/generate-code")
async def generate_code(request: GenerateCodeRequest):
    """
    Generate code using Codegen
    """
    ui = get_ui()
    return ui.generate_code(request.prompt, request.language)

@app.post("/api/codegen/analyze-code")
async def analyze_code(request: AnalyzeCodeRequest):
    """
    Analyze code using Codegen
    """
    ui = get_ui()
    return ui.analyze_code(request.code, request.language)

@app.post("/api/codegen/refactor-code")
async def refactor_code(request: RefactorCodeRequest):
    """
    Refactor code using Codegen
    """
    ui = get_ui()
    return ui.refactor_code(request.code, request.language, request.instructions)

@app.post("/api/codegen/generate-tests")
async def generate_tests(request: GenerateTestsRequest):
    """
    Generate tests for code using Codegen
    """
    ui = get_ui()
    return ui.generate_tests(request.code, request.language)

@app.get("/api/codegen/context")
async def get_context():
    """
    Get shared context between TaskWeaver and Codegen
    """
    ui = get_ui()
    return ui.get_shared_context()

@app.post("/api/codegen/context/taskweaver")
async def update_taskweaver_context(request: ContextUpdateRequest):
    """
    Update TaskWeaver context
    """
    ui = get_ui()
    return ui.update_taskweaver_context(request.context)

@app.post("/api/codegen/context/codegen")
async def update_codegen_context(request: ContextUpdateRequest):
    """
    Update Codegen context
    """
    ui = get_ui()
    return ui.update_codegen_context(request.context)

@app.post("/api/codegen/context/issue")
async def add_issue_to_context(request: IssueRequest):
    """
    Add a GitHub issue to the context
    """
    ui = get_ui()
    return ui.add_issue_to_context(request.issue_number)

@app.post("/api/codegen/context/pr")
async def add_pr_to_context(request: PrRequest):
    """
    Add a GitHub pull request to the context
    """
    ui = get_ui()
    return ui.add_pr_to_context(request.pr_number)

@app.post("/api/codegen/context/file")
async def add_file_to_context(request: FileRequest):
    """
    Add a file to the context
    """
    ui = get_ui()
    return ui.add_file_to_context(request.file_path)

@app.post("/api/codegen/requirements")
async def create_requirements(request: RequirementsRequest):
    """
    Create or update a REQUIREMENTS.md file in the repository
    """
    ui = get_ui()
    return ui.create_requirements_document(request.requirements)

@app.post("/api/codegen/workflow/start")
async def start_workflow():
    """
    Start the Codegen workflow
    """
    ui = get_ui()
    return ui.start_workflow()

@app.post("/api/codegen/workflow/stop")
async def stop_workflow():
    """
    Stop the Codegen workflow
    """
    ui = get_ui()
    return ui.stop_workflow()

@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the server
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Create a temporary file
        temp_dir = os.path.join(current_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, file.filename)
        
        # Write the file
        with open(file_path, "wb") as f:
            f.write(content)
            
        return {"status": "success", "filename": file.filename, "path": file_path}
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return {"status": "error", "message": str(e)}

def run_server(host: str = "0.0.0.0", port: int = 8000, public: bool = False):
    """
    Run the server
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        public: Whether to make the server publicly accessible via ngrok
    """
    if public:
        try:
            from pyngrok import ngrok
            
            # Get ngrok token from environment
            ngrok_token = os.environ.get("NGROK_TOKEN")
            if ngrok_token:
                ngrok.set_auth_token(ngrok_token)
                
            # Start ngrok tunnel
            public_url = ngrok.connect(port)
            logger.info(f"Public URL: {public_url}")
        except ImportError:
            logger.warning("pyngrok not installed. Cannot create public URL.")
            logger.warning("Install pyngrok with: pip install pyngrok")
        except Exception as e:
            logger.error(f"Error starting ngrok tunnel: {str(e)}")
            
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()

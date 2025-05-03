"""
Enhanced web server for TaskWeaver UI with Codegen agent integration
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
from standalone_taskweaver.codegen_agent.bidirectional_context import BidirectionalContext
from standalone_taskweaver.codegen_agent.advanced_api import CodegenAdvancedAPI
from standalone_taskweaver.ui.taskweaver_ui_enhanced import TaskWeaverUIEnhanced

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-ui-enhanced")

# Create FastAPI app
app = FastAPI(title="TaskWeaver UI Enhanced")

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

# Create TaskWeaverUIEnhanced instance
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

class ProjectContextRequest(BaseModel):
    project_name: str
    project_description: str
    requirements_text: str

class DeploymentPlanRequest(BaseModel):
    deployment_plan: str

class ExecuteStepsRequest(BaseModel):
    max_concurrent_steps: int = 1

class ExecuteSingleStepRequest(BaseModel):
    step_id: str
    step_title: str
    step_description: str

class StepIdRequest(BaseModel):
    step_id: str

# Initialize UI
def get_ui():
    global ui
    if ui is None:
        ui = TaskWeaverUIEnhanced(None, None, None)
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

# New weaver integration endpoints

@app.post("/api/weaver/project-context")
async def set_project_context(request: ProjectContextRequest):
    """
    Set the project context for the Codegen agent
    """
    ui = get_ui()
    return ui.set_project_context(
        project_name=request.project_name,
        project_description=request.project_description,
        requirements_text=request.requirements_text
    )

@app.post("/api/weaver/deployment-steps")
async def parse_deployment_steps(request: DeploymentPlanRequest):
    """
    Parse deployment steps from a deployment plan
    """
    ui = get_ui()
    return ui.parse_deployment_steps(request.deployment_plan)

@app.post("/api/weaver/execute-steps")
async def execute_deployment_steps(request: ExecuteStepsRequest):
    """
    Execute deployment steps
    """
    ui = get_ui()
    return ui.execute_deployment_steps(max_concurrent_steps=request.max_concurrent_steps)

@app.post("/api/weaver/execute-step")
async def execute_single_step(request: ExecuteSingleStepRequest):
    """
    Execute a single deployment step
    """
    ui = get_ui()
    return ui.execute_single_step(
        step_id=request.step_id,
        step_title=request.step_title,
        step_description=request.step_description
    )

@app.get("/api/weaver/step/{step_id}/status")
async def get_step_status(step_id: str):
    """
    Get the status of a deployment step
    """
    ui = get_ui()
    return ui.get_step_status(step_id)

@app.get("/api/weaver/step/{step_id}/result")
async def get_step_result(step_id: str):
    """
    Get the result of a deployment step
    """
    ui = get_ui()
    return ui.get_step_result(step_id)

@app.get("/api/weaver/steps/results")
async def get_all_step_results():
    """
    Get all deployment step results
    """
    ui = get_ui()
    return ui.get_all_step_results()

@app.get("/api/weaver/status")
async def get_weaver_status():
    """
    Get the status of the weaver integration
    """
    ui = get_ui()
    return ui.get_weaver_status()

@app.post("/api/weaver/cancel")
async def cancel_all_steps():
    """
    Cancel all running deployment steps
    """
    ui = get_ui()
    return ui.cancel_all_steps()

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the server
    """
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()


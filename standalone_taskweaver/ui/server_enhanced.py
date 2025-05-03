#!/usr/bin/env python3
"""
Enhanced web server for TaskWeaver UI with multithreaded execution support
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, Depends, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from injector import inject

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.app.session_manager import SessionManager
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.module.tracing import Tracing
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
}

# Create AppConfigSource
config = AppConfigSource()

# Create dependencies for TaskWeaver app
telemetry_logger = TelemetryLogger(config)
session_manager = SessionManager(config, telemetry_logger)
tracing = Tracing(config, telemetry_logger)

# Create TaskWeaver app with proper dependencies
taskweaver_app = TaskWeaverApp(
    config=config,
    session_manager=session_manager,
    logger=telemetry_logger,
    tracing=tracing
)

# Create TaskWeaver UI
ui = TaskWeaverUIEnhanced(taskweaver_app, config, telemetry_logger)

# WebSocket connections
active_connections: List[WebSocket] = []

# Request models
class MessageRequest(BaseModel):
    content: str

class ProjectContextRequest(BaseModel):
    project_name: str
    project_description: str

class ExecuteTasksRequest(BaseModel):
    max_concurrent_tasks: int = 3

class ApiCredentialsRequest(BaseModel):
    github_token: Optional[str] = None
    codegen_token: Optional[str] = None
    ngrok_token: Optional[str] = None

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Get the index page
    """
    return templates.TemplateResponse("index_enhanced.html", {"request": request})

@app.post("/api/credentials")
async def set_credentials(request: ApiCredentialsRequest):
    """
    Set API credentials
    """
    global api_credentials
    
    # Update credentials
    if request.github_token:
        api_credentials["github_token"] = request.github_token
    
    if request.codegen_token:
        api_credentials["codegen_token"] = request.codegen_token
        # Initialize Codegen agent
        ui.initialize_agent(request.codegen_token)
    
    if request.ngrok_token:
        api_credentials["ngrok_token"] = request.ngrok_token
    
    return {"status": "success"}

@app.get("/api/credentials")
async def get_credentials():
    """
    Get API credentials status
    """
    return {
        "github_token": bool(api_credentials["github_token"]),
        "codegen_token": bool(api_credentials["codegen_token"]),
        "ngrok_token": bool(api_credentials["ngrok_token"]),
    }

@app.post("/api/chat/message")
async def add_message(request: MessageRequest):
    """
    Add a message to the chat
    """
    # Add message to chat history
    ui.add_message("user", request.content)
    
    # Generate response
    response = "I've received your message and updated the requirements. When you're satisfied with the plan, press Initialize to start the implementation."
    ui.add_message("assistant", response)
    
    return {"status": "success", "response": response}

@app.get("/api/chat/history")
async def get_chat_history():
    """
    Get chat history
    """
    return {"history": ui.get_chat_history()}

@app.post("/api/project/context")
async def set_project_context(request: ProjectContextRequest):
    """
    Set project context
    """
    ui.set_project_context(request.project_name, request.project_description)
    
    return {"status": "success"}

@app.get("/api/requirements")
async def get_requirements():
    """
    Get requirements
    """
    return ui.get_requirements()

@app.post("/api/tasks/execute")
async def execute_tasks(request: ExecuteTasksRequest):
    """
    Execute tasks
    """
    # Start task execution
    ui.execute_tasks(request.max_concurrent_tasks)
    
    return {"status": "success"}

@app.get("/api/tasks/status")
async def get_task_status():
    """
    Get task execution status
    """
    return ui.get_execution_status()

@app.post("/api/tasks/cancel")
async def cancel_tasks():
    """
    Cancel task execution
    """
    result = ui.cancel_execution()
    
    return {"status": "success" if result else "error"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Wait for messages
            data = await websocket.receive_text()
            
            # Process message
            message = json.loads(data)
            
            if message["type"] == "ping":
                # Send status update
                await websocket.send_json({
                    "type": "status",
                    "data": ui.get_execution_status()
                })
            
            # Sleep to avoid high CPU usage
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if websocket in active_connections:
            active_connections.remove(websocket)

async def broadcast_status():
    """
    Broadcast status updates to all connected clients
    """
    while True:
        if active_connections:
            # Get current status
            status = ui.get_execution_status()
            
            # Broadcast to all connections
            for connection in active_connections:
                try:
                    await connection.send_json({
                        "type": "status",
                        "data": status
                    })
                except Exception as e:
                    logger.error(f"Error broadcasting status: {str(e)}")
        
        # Wait before next update
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    """
    Startup event
    """
    # Start background task for broadcasting status
    asyncio.create_task(broadcast_status())

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the server
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
    """
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()

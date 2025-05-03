"""
TaskWeaver Web UI Server
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def run_server(host: str = "0.0.0.0", port: int = 8000, config_path: Optional[str] = None):
    """
    Run the TaskWeaver web server
    
    Args:
        host: Host to bind the web server to
        port: Port to bind the web server to
        config_path: Path to configuration file
        
    Returns:
        int: Exit code
    """
    try:
        # Apply configuration if provided
        if config_path:
            if not os.path.exists(config_path):
                logger.error(f"Configuration file not found: {config_path}")
                return 1
            os.environ["TASKWEAVER_CONFIG_PATH"] = config_path
            logger.info(f"Using configuration from {config_path}")
        
        # Import FastAPI components
        try:
            from fastapi import FastAPI
            from fastapi.staticfiles import StaticFiles
            from fastapi.templating import Jinja2Templates
            import uvicorn
        except ImportError:
            logger.error("FastAPI and uvicorn are required for the web UI")
            logger.error("Install them with: pip install fastapi uvicorn jinja2")
            return 1
        
        # Create FastAPI app
        app = FastAPI(
            title="TaskWeaver",
            description="A code-first agent framework for data analytics tasks",
            version="0.1.0",
        )
        
        # Mount static files
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
        # Set up templates
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
        if os.path.exists(templates_dir):
            templates = Jinja2Templates(directory=templates_dir)
        
        # Define routes
        @app.get("/")
        async def root():
            return {"message": "Welcome to TaskWeaver API"}
        
        # Run the server
        logger.info(f"Starting TaskWeaver Web UI on http://{host}:{port}")
        logger.info("Press Ctrl+C to stop the server")
        
        uvicorn.run(app, host=host, port=port)
        return 0
    except Exception as e:
        logger.error(f"Error launching web UI: {str(e)}")
        return 1


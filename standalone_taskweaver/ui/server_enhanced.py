#!/usr/bin/env python3
"""
Enhanced server implementation with deployment endpoints
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from standalone_taskweaver.app.app import TaskWeaverApp
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.ui.taskweaver_ui_enhanced import TaskWeaverUIEnhanced

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("taskweaver-server-enhanced")

class TaskWeaverServerEnhanced:
    """
    Enhanced TaskWeaver server implementation with deployment endpoints
    """
    
    def __init__(
        self,
        app: TaskWeaverApp,
        config: AppConfigSource,
        logger: TelemetryLogger,
        ui: Optional[TaskWeaverUIEnhanced] = None,
        host: str = "0.0.0.0",
        port: int = 5000,
    ) -> None:
        self.app = app
        self.config = config
        self.logger = logger
        self.ui = ui or TaskWeaverUIEnhanced(app, config, logger)
        self.host = host
        self.port = port
        
        # Create Flask app
        self.flask_app = Flask(__name__)
        CORS(self.flask_app)
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self) -> None:
        """
        Register routes for the Flask app
        """
        # Static files
        @self.flask_app.route("/")
        def index():
            return send_from_directory("static", "index.html")
        
        @self.flask_app.route("/<path:path>")
        def static_files(path):
            return send_from_directory("static", path)
        
        # API endpoints
        @self.flask_app.route("/api/status", methods=["GET"])
        def status():
            return jsonify({
                "status": "ok",
                "integration": self.ui.get_integration_status()
            })
        
        @self.flask_app.route("/api/initialize", methods=["POST"])
        def initialize():
            data = request.json
            
            github_token = data.get("github_token")
            codegen_token = data.get("codegen_token")
            ngrok_token = data.get("ngrok_token")
            codegen_org_id = data.get("codegen_org_id")
            
            if not github_token or not codegen_token or not ngrok_token or not codegen_org_id:
                return jsonify({
                    "status": "error",
                    "message": "Missing required parameters"
                }), 400
            
            success = self.ui.initialize_integration(
                github_token=github_token,
                codegen_token=codegen_token,
                ngrok_token=ngrok_token,
                codegen_org_id=codegen_org_id
            )
            
            if success:
                return jsonify({
                    "status": "ok",
                    "message": "Integration initialized successfully"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Failed to initialize integration"
                }), 500
        
        # GitHub endpoints
        @self.flask_app.route("/api/github/repos", methods=["GET"])
        def github_repos():
            return jsonify({
                "status": "ok",
                "repos": self.ui.get_github_repos()
            })
        
        @self.flask_app.route("/api/github/repos/<repo_name>", methods=["GET"])
        def github_repo(repo_name):
            return jsonify({
                "status": "ok",
                "repo": self.ui.get_github_repo(repo_name)
            })
        
        @self.flask_app.route("/api/github/repos/<repo_name>/files", methods=["GET"])
        def github_repo_files(repo_name):
            path = request.args.get("path", "")
            
            return jsonify({
                "status": "ok",
                "files": self.ui.get_github_repo_files(repo_name, path)
            })
        
        @self.flask_app.route("/api/github/repos/<repo_name>/files/<path:file_path>", methods=["GET"])
        def github_file_content(repo_name, file_path):
            return jsonify({
                "status": "ok",
                "content": self.ui.get_github_file_content(repo_name, file_path)
            })
        
        @self.flask_app.route("/api/github/search", methods=["GET"])
        def github_search():
            query = request.args.get("query", "")
            
            if not query:
                return jsonify({
                    "status": "error",
                    "message": "Missing query parameter"
                }), 400
            
            return jsonify({
                "status": "ok",
                "results": self.ui.search_github_code(query)
            })
        
        # Codegen endpoints
        @self.flask_app.route("/api/codegen/is-code-related", methods=["POST"])
        def is_code_related():
            data = request.json
            
            task_description = data.get("task_description")
            
            if not task_description:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_description parameter"
                }), 400
            
            return jsonify({
                "status": "ok",
                "is_code_related": self.ui.is_code_related_task(task_description)
            })
        
        @self.flask_app.route("/api/codegen/delegate", methods=["POST"])
        def delegate_to_codegen():
            data = request.json
            
            task_description = data.get("task_description")
            context = data.get("context", {})
            
            if not task_description:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_description parameter"
                }), 400
            
            try:
                result = self.ui.delegate_to_codegen(task_description, context)
                
                return jsonify({
                    "status": "ok",
                    "result": result
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        # Deployment endpoints
        @self.flask_app.route("/api/codegen/deployment/is-deployment-task", methods=["POST"])
        def is_deployment_task():
            data = request.json
            
            task_description = data.get("task_description")
            
            if not task_description:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_description parameter"
                }), 400
            
            return jsonify({
                "status": "ok",
                "is_deployment_task": self.ui.is_deployment_task(task_description)
            })
        
        @self.flask_app.route("/api/codegen/deployment/create", methods=["POST"])
        def create_deployment_task():
            data = request.json
            
            task_description = data.get("task_description")
            context = data.get("context", {})
            
            if not task_description:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_description parameter"
                }), 400
            
            try:
                task_id = self.ui.create_deployment_task(task_description, context)
                
                return jsonify({
                    "status": "ok",
                    "task_id": task_id
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.flask_app.route("/api/codegen/deployment/delegate", methods=["POST"])
        def delegate_deployment_task():
            data = request.json
            
            task_id = data.get("task_id")
            
            if not task_id:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_id parameter"
                }), 400
            
            try:
                success = self.ui.delegate_deployment_task(task_id)
                
                if success:
                    return jsonify({
                        "status": "ok",
                        "message": "Task delegated successfully"
                    })
                else:
                    return jsonify({
                        "status": "error",
                        "message": "Failed to delegate task"
                    }), 500
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.flask_app.route("/api/codegen/deployment/status", methods=["GET"])
        def get_deployment_task_status():
            task_id = request.args.get("task_id")
            
            if not task_id:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_id parameter"
                }), 400
            
            try:
                task_status = self.ui.get_deployment_task_status(task_id)
                
                return jsonify({
                    "status": "ok",
                    "task_status": task_status
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.flask_app.route("/api/codegen/deployment/results", methods=["GET"])
        def get_deployment_task_results():
            task_id = request.args.get("task_id")
            
            if not task_id:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_id parameter"
                }), 400
            
            try:
                task_results = self.ui.get_deployment_task_results(task_id)
                
                return jsonify({
                    "status": "ok",
                    "task_results": task_results
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.flask_app.route("/api/codegen/deployment/report", methods=["GET"])
        def generate_deployment_report():
            task_id = request.args.get("task_id")
            
            if not task_id:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_id parameter"
                }), 400
            
            try:
                report = self.ui.generate_deployment_report(task_id)
                
                return jsonify({
                    "status": "ok",
                    "report": report
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.flask_app.route("/api/codegen/deployment/add-to-memory", methods=["POST"])
        def add_deployment_to_memory():
            data = request.json
            
            task_id = data.get("task_id")
            planner_id = data.get("planner_id")
            
            if not task_id or not planner_id:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_id or planner_id parameter"
                }), 400
            
            try:
                success = self.ui.add_deployment_to_memory(task_id, planner_id)
                
                if success:
                    return jsonify({
                        "status": "ok",
                        "message": "Task added to memory successfully"
                    })
                else:
                    return jsonify({
                        "status": "error",
                        "message": "Failed to add task to memory"
                    }), 500
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.flask_app.route("/api/codegen/deployment/cancel", methods=["POST"])
        def cancel_deployment_task():
            data = request.json
            
            task_id = data.get("task_id")
            
            if not task_id:
                return jsonify({
                    "status": "error",
                    "message": "Missing task_id parameter"
                }), 400
            
            try:
                success = self.ui.cancel_deployment_task(task_id)
                
                if success:
                    return jsonify({
                        "status": "ok",
                        "message": "Task cancelled successfully"
                    })
                else:
                    return jsonify({
                        "status": "error",
                        "message": "Failed to cancel task"
                    }), 500
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
        
        @self.flask_app.route("/api/codegen/deployment/list", methods=["GET"])
        def list_deployment_tasks():
            try:
                tasks = self.ui.list_deployment_tasks()
                
                return jsonify({
                    "status": "ok",
                    "tasks": tasks
                })
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": str(e)
                }), 500
    
    def run(self) -> None:
        """
        Run the server
        """
        self.flask_app.run(host=self.host, port=self.port, debug=False)


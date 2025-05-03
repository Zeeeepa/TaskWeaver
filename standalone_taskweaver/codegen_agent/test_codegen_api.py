#!/usr/bin/env python3
"""
Test script for the upgraded Codegen API integration.
This script verifies that all the main functionality of the Codegen integration works correctly.
"""

import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from standalone_taskweaver.codegen_agent.codegen import CodegenManager
from standalone_taskweaver.codegen_agent.integration import CodegenIntegration
from standalone_taskweaver.codegen_agent.advanced_api import CodegenAdvancedAPI


class MockTask:
    """Mock Task class for testing."""
    
    def __init__(self, status="completed"):
        self.status = status
        self.id = "mock-task-id"
        self.result = {"code": "def test(): return 'Hello, World!'"}
    
    def refresh(self):
        """Mock refresh method."""
        pass


class TestCodegenAPI(unittest.TestCase):
    """Test cases for the Codegen API integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_token = "mock-token"
        self.mock_org_id = "mock-org-id"
        
        # Create patch for the Agent class
        self.agent_patcher = patch('standalone_taskweaver.codegen_agent.codegen.Agent')
        self.mock_agent_class = self.agent_patcher.start()
        self.mock_agent = self.mock_agent_class.return_value
        self.mock_agent.create_task.return_value = MockTask()
        
        # Initialize the classes with the mock agent
        self.codegen_manager = CodegenManager(
            codegen_token=self.mock_token,
            org_id=self.mock_org_id
        )
        self.codegen_integration = CodegenIntegration(
            codegen_token=self.mock_token,
            org_id=self.mock_org_id
        )
        self.advanced_api = CodegenAdvancedAPI(
            codegen_token=self.mock_token,
            org_id=self.mock_org_id
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.agent_patcher.stop()
    
    def test_codegen_manager_initialization(self):
        """Test that the CodegenManager initializes correctly."""
        self.assertEqual(self.codegen_manager.codegen_token, self.mock_token)
        self.assertEqual(self.codegen_manager.org_id, self.mock_org_id)
        self.assertIsNotNone(self.codegen_manager.codegen_agent)
    
    def test_codegen_integration_initialization(self):
        """Test that the CodegenIntegration initializes correctly."""
        self.assertEqual(self.codegen_integration.codegen_token, self.mock_token)
        self.assertEqual(self.codegen_integration.org_id, self.mock_org_id)
        self.assertIsNotNone(self.codegen_integration.codegen_agent)
    
    def test_advanced_api_initialization(self):
        """Test that the CodegenAdvancedAPI initializes correctly."""
        self.assertEqual(self.advanced_api.codegen_token, self.mock_token)
        self.assertEqual(self.advanced_api.org_id, self.mock_org_id)
        self.assertIsNotNone(self.advanced_api.codegen_agent)
    
    def test_run_codegen_task(self):
        """Test that run_codegen_task works correctly."""
        task = self.codegen_integration.run_codegen_task("Generate a function")
        self.assertEqual(task.id, "mock-task-id")
        self.assertEqual(task.status, "completed")
    
    def test_get_task_status(self):
        """Test that get_task_status works correctly."""
        task = MockTask()
        status = self.codegen_integration.get_task_status(task)
        self.assertEqual(status, "completed")
    
    def test_get_task_result(self):
        """Test that get_task_result works correctly."""
        task = MockTask()
        result = self.codegen_integration.get_task_result(task)
        self.assertEqual(result, {"code": "def test(): return 'Hello, World!'"})
    
    def test_analyze_code(self):
        """Test that analyze_code works correctly."""
        with patch.object(self.advanced_api, 'run_codegen_task') as mock_run:
            mock_run.return_value = MockTask()
            result = self.advanced_api.analyze_code("def test(): pass")
            self.assertEqual(result, {"code": "def test(): return 'Hello, World!'"})
    
    def test_generate_tests(self):
        """Test that generate_tests works correctly."""
        with patch.object(self.advanced_api, 'run_codegen_task') as mock_run:
            mock_run.return_value = MockTask()
            result = self.advanced_api.generate_tests("def test(): pass")
            self.assertEqual(result, {"code": "def test(): return 'Hello, World!'"})
    
    def test_refactor_code(self):
        """Test that refactor_code works correctly."""
        with patch.object(self.advanced_api, 'run_codegen_task') as mock_run:
            mock_run.return_value = MockTask()
            result = self.advanced_api.refactor_code("def test(): pass")
            self.assertEqual(result, {"code": "def test(): return 'Hello, World!'"})
    
    def test_error_handling(self):
        """Test error handling when a task fails."""
        # Create a failed task
        failed_task = MockTask(status="failed")
        
        # Mock the run_codegen_task to return the failed task
        with patch.object(self.codegen_integration, 'run_codegen_task') as mock_run:
            mock_run.return_value = failed_task
            
            # Test that the error is handled correctly
            with patch.object(self.codegen_integration, 'logger') as mock_logger:
                result = self.codegen_integration.run_task("Generate a function")
                mock_logger.error.assert_called_once()
                self.assertEqual(result, {"success": False, "error": "Task failed: failed"})


if __name__ == '__main__':
    unittest.main()


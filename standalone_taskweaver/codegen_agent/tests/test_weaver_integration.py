#!/usr/bin/env python3
"""
Tests for the Codegen Weaver Integration
"""

import unittest
from unittest.mock import MagicMock, patch
import asyncio

from standalone_taskweaver.codegen_agent.weaver_integration import CodegenWeaverIntegration
from standalone_taskweaver.codegen_agent.requirements_manager import AtomicTask
from standalone_taskweaver.codegen_agent.concurrent_execution import TaskStatus, TaskResult

class TestCodegenWeaverIntegration(unittest.TestCase):
    """
    Test cases for the CodegenWeaverIntegration class
    """
    
    def setUp(self):
        """
        Set up test fixtures
        """
        # Create mocks
        self.app_mock = MagicMock()
        self.config_mock = MagicMock()
        self.logger_mock = MagicMock()
        self.memory_mock = MagicMock()
        self.codegen_agent_mock = MagicMock()
        
        # Create integration with mocks
        self.integration = CodegenWeaverIntegration(
            app=self.app_mock,
            config=self.config_mock,
            logger=self.logger_mock,
            memory=self.memory_mock,
            codegen_agent=self.codegen_agent_mock
        )
        
        # Set up codegen_agent mock
        self.codegen_agent_mock.initialize.return_value = True
        
    def test_initialize(self):
        """
        Test initialization of the integration
        """
        # Test successful initialization
        result = self.integration.initialize("test-token")
        self.assertTrue(result)
        self.assertTrue(self.integration.is_initialized)
        self.codegen_agent_mock.initialize.assert_called_once_with("test-token")
        
        # Test failed initialization
        self.codegen_agent_mock.initialize.return_value = False
        result = self.integration.initialize("test-token")
        self.assertFalse(result)
        
        # Test exception handling
        self.codegen_agent_mock.initialize.side_effect = Exception("Test error")
        result = self.integration.initialize("test-token")
        self.assertFalse(result)
        self.logger_mock.error.assert_called()
        
    def test_set_project_context(self):
        """
        Test setting project context
        """
        # Set up
        self.integration.is_initialized = True
        
        # Test valid input
        self.integration.set_project_context(
            project_name="Test Project",
            project_description="Test Description",
            requirements_text="Test Requirements"
        )
        self.codegen_agent_mock.set_project_context.assert_called_once_with(
            project_name="Test Project",
            project_description="Test Description",
            requirements_text="Test Requirements"
        )
        self.assertEqual(self.integration.current_project, "Test Project")
        
        # Test not initialized
        self.integration.is_initialized = False
        with self.assertRaises(ValueError):
            self.integration.set_project_context(
                project_name="Test Project",
                project_description="Test Description",
                requirements_text="Test Requirements"
            )
            
        # Test invalid input
        self.integration.is_initialized = True
        with self.assertRaises(ValueError):
            self.integration.set_project_context(
                project_name="",
                project_description="Test Description",
                requirements_text="Test Requirements"
            )
            
    def test_parse_deployment_steps(self):
        """
        Test parsing deployment steps
        """
        # Set up
        self.integration.is_initialized = True
        
        # Test valid input
        deployment_plan = """
        Step 1: Initialize the project
        Create a new directory and initialize a Git repository.
        
        Step 2: Install dependencies
        Install the required dependencies using npm.
        """
        
        steps = self.integration.parse_deployment_steps(deployment_plan)
        
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0].id, "step-1")
        self.assertEqual(steps[0].title, "Step 1: Initialize the project")
        self.assertEqual(steps[1].id, "step-2")
        self.assertEqual(steps[1].title, "Step 2: Install dependencies")
        
        # Test not initialized
        self.integration.is_initialized = False
        with self.assertRaises(ValueError):
            self.integration.parse_deployment_steps(deployment_plan)
            
    def test_execute_deployment_steps(self):
        """
        Test executing deployment steps
        """
        # Set up
        self.integration.is_initialized = True
        self.integration.deployment_steps = [
            AtomicTask(
                id="step-1",
                title="Step 1",
                description="Description 1",
                priority=1,
                dependencies=[],
                phase=1,
                status="pending",
                tags=["deployment"],
                estimated_time=0,
                assignee=None,
                interface_definition=False
            ),
            AtomicTask(
                id="step-2",
                title="Step 2",
                description="Description 2",
                priority=2,
                dependencies=["step-1"],
                phase=1,
                status="pending",
                tags=["deployment"],
                estimated_time=0,
                assignee=None,
                interface_definition=False
            )
        ]
        
        # Mock execution results
        mock_results = {
            "step-1": TaskResult(
                id="step-1",
                status=TaskStatus.COMPLETED,
                result="Result 1",
                error=None,
                start_time=0,
                end_time=1,
                duration=1
            ),
            "step-2": TaskResult(
                id="step-2",
                status=TaskStatus.COMPLETED,
                result="Result 2",
                error=None,
                start_time=1,
                end_time=2,
                duration=1
            )
        }
        self.codegen_agent_mock.execute_tasks.return_value = mock_results
        
        # Test execution
        results = self.integration.execute_deployment_steps(max_concurrent_steps=2)
        
        self.assertEqual(results, mock_results)
        self.codegen_agent_mock.execute_tasks.assert_called_once_with(max_concurrent_tasks=2)
        
        # Test not initialized
        self.integration.is_initialized = False
        with self.assertRaises(ValueError):
            self.integration.execute_deployment_steps(max_concurrent_steps=2)
            
        # Test no steps
        self.integration.is_initialized = True
        self.integration.deployment_steps = []
        with self.assertRaises(ValueError):
            self.integration.execute_deployment_steps(max_concurrent_steps=2)
            
    def test_execute_single_step(self):
        """
        Test executing a single step
        """
        # Set up
        self.integration.is_initialized = True
        
        # Mock execution result
        mock_result = TaskResult(
            id="test-step",
            status=TaskStatus.COMPLETED,
            result="Test Result",
            error=None,
            start_time=0,
            end_time=1,
            duration=1
        )
        self.codegen_agent_mock.execute_single_task.return_value = mock_result
        
        # Test execution
        result = self.integration.execute_single_step(
            step_id="test-step",
            step_title="Test Step",
            step_description="Test Description"
        )
        
        self.assertEqual(result, mock_result)
        self.codegen_agent_mock.execute_single_task.assert_called_once()
        
        # Test not initialized
        self.integration.is_initialized = False
        with self.assertRaises(ValueError):
            self.integration.execute_single_step(
                step_id="test-step",
                step_title="Test Step",
                step_description="Test Description"
            )
            
        # Test invalid input
        self.integration.is_initialized = True
        with self.assertRaises(ValueError):
            self.integration.execute_single_step(
                step_id="",
                step_title="Test Step",
                step_description="Test Description"
            )
            
    def test_memory_management(self):
        """
        Test memory management
        """
        # Set up
        self.integration.max_stored_results = 2
        
        # Add more results than the limit
        self.integration._manage_results_storage({
            "step-1": {"result": "Result 1", "timestamp": 1},
            "step-2": {"result": "Result 2", "timestamp": 2},
            "step-3": {"result": "Result 3", "timestamp": 3}
        })
        
        # Check that the oldest result was removed
        self.assertEqual(len(self.integration.step_results), 2)
        self.assertIn("step-2", self.integration.step_results)
        self.assertIn("step-3", self.integration.step_results)
        self.assertNotIn("step-1", self.integration.step_results)
        
    def test_get_status(self):
        """
        Test getting status
        """
        # Set up
        self.integration.is_initialized = True
        self.integration.current_project = "Test Project"
        self.integration.deployment_steps = [MagicMock(), MagicMock()]
        
        # Mock agent status
        mock_status = {"status": "running"}
        self.codegen_agent_mock.get_status.return_value = mock_status
        
        # Test getting status
        status = self.integration.get_status()
        
        self.assertEqual(status["status"], "running")
        self.assertEqual(status["deployment_steps"], 2)
        self.assertEqual(status["current_project"], "Test Project")
        
    def test_cancel_all_steps(self):
        """
        Test cancelling all steps
        """
        # Set up
        self.integration.is_initialized = True
        self.codegen_agent_mock.cancel_all_tasks.return_value = True
        
        # Test cancellation
        result = self.integration.cancel_all_steps()
        
        self.assertTrue(result)
        self.codegen_agent_mock.cancel_all_tasks.assert_called_once()

if __name__ == "__main__":
    unittest.main()


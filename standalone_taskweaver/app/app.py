import os
from typing import Dict, Optional

from injector import Injector, inject

from standalone_taskweaver.app.session_manager import SessionManager
from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Memory
from standalone_taskweaver.module.tracing import Tracing
from standalone_taskweaver.session.session import Session, SessionMetadata


class TaskWeaverApp:
    """
    TaskWeaverApp is the main application class.
    """

    @inject
    def __init__(
        self,
        config: AppConfigSource,
        session_manager: SessionManager,
        logger: TelemetryLogger,
        tracing: Tracing,
    ) -> None:
        self.config = config
        self.session_manager = session_manager
        self.logger = logger
        self.tracing = tracing

        self.logger.info("TaskWeaverApp initialized successfully")

    def create_session(
        self,
        session_id: Optional[str] = None,
        session_name: Optional[str] = None,
        session_dir: Optional[str] = None,
        session_variables: Optional[Dict[str, str]] = None,
    ) -> Session:
        """
        Create a session.
        :param session_id: The session ID.
        :param session_name: The session name.
        :param session_dir: The session directory.
        :param session_variables: The session variables.
        :return: The session.
        """
        if session_dir is None:
            session_dir = os.path.join(self.config.app_base_path, "sessions")
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        session = self.session_manager.create_session(
            session_id=session_id,
            session_name=session_name,
            session_dir=session_dir,
            session_variables=session_variables,
        )
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session.
        :param session_id: The session ID.
        :return: The session.
        """
        return self.session_manager.get_session(session_id)

    def list_sessions(self) -> Dict[str, Session]:
        """
        List all sessions.
        :return: The sessions.
        """
        return self.session_manager.list_sessions()

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        :param session_id: The session ID.
        :return: Whether the session was deleted.
        """
        return self.session_manager.delete_session(session_id)

    def chat(
        self,
        session_id: str,
        message: str,
    ) -> str:
        """
        Chat with a session.
        :param session_id: The session ID.
        :param message: The message.
        :return: The response.
        """
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        response = session.chat(message)
        return response


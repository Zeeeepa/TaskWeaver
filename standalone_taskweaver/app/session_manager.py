import os
import uuid
from typing import Dict, Optional

from injector import Injector, inject

from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.module.tracing import Tracing
from standalone_taskweaver.session.session import Session, SessionMetadata


class SessionManager:
    """
    SessionManager is used to manage sessions.
    """

    @inject
    def __init__(
        self,
        config: AppConfigSource,
        logger: TelemetryLogger,
        tracing: Tracing,
    ) -> None:
        self.config = config
        self.logger = logger
        self.tracing = tracing
        self.sessions: Dict[str, Session] = {}

        self.logger.info("SessionManager initialized successfully")

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
        if session_id is None:
            session_id = str(uuid.uuid4())
        if session_name is None:
            session_name = f"Session {session_id}"
        if session_dir is None:
            session_dir = os.path.join(self.config.app_base_path, "sessions")
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        session_metadata = SessionMetadata(
            session_id=session_id,
            session_name=session_name,
            session_dir=os.path.join(session_dir, session_id),
            execution_cwd=os.path.join(session_dir, session_id, "workspace"),
        )

        # create the session directory
        if not os.path.exists(session_metadata.session_dir):
            os.makedirs(session_metadata.session_dir)
        # create the execution directory
        if not os.path.exists(session_metadata.execution_cwd):
            os.makedirs(session_metadata.execution_cwd)

        # create a new injector for the session
        session_injector = Injector()
        session_injector.binder.bind(SessionMetadata, to=session_metadata)
        session_injector.binder.bind(AppConfigSource, to=self.config)
        session_injector.binder.bind(TelemetryLogger, to=self.logger)
        session_injector.binder.bind(Tracing, to=self.tracing)

        # create the session
        session = session_injector.create_object(Session)
        if session_variables is not None:
            session.update_session_variables(session_variables)

        # add the session to the sessions
        self.sessions[session_id] = session

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session.
        :param session_id: The session ID.
        :return: The session.
        """
        return self.sessions.get(session_id)

    def list_sessions(self) -> Dict[str, Session]:
        """
        List all sessions.
        :return: The sessions.
        """
        return self.sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        :param session_id: The session ID.
        :return: Whether the session was deleted.
        """
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.close()
        del self.sessions[session_id]

        return True


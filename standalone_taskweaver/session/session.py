import os
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

from injector import inject

from standalone_taskweaver.code_interpreter import CodeInterpreter
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Memory, Post, Round
from standalone_taskweaver.module.event_emitter import SessionEventEmitter
from standalone_taskweaver.module.tracing import Tracing, tracing_decorator
from standalone_taskweaver.planner import Planner


@dataclass
class SessionMetadata:
    """
    SessionMetadata is used to store the metadata of a session.
    """

    session_id: str
    session_name: str
    session_dir: str
    execution_cwd: str


class Session:
    """
    Session is used to manage a conversation session.
    """

    @inject
    def __init__(
        self,
        session_metadata: SessionMetadata,
        logger: TelemetryLogger,
        tracing: Tracing,
        event_emitter: SessionEventEmitter,
        planner: Planner,
        code_interpreter: CodeInterpreter,
    ) -> None:
        self.session_metadata = session_metadata
        self.logger = logger
        self.tracing = tracing
        self.event_emitter = event_emitter
        self.planner = planner
        self.code_interpreter = code_interpreter

        self.memory = Memory()
        self.session_variables: Dict[str, str] = {}

        self.logger.info(f"Session {session_metadata.session_id} initialized successfully")

    def update_session_variables(self, session_variables: Dict[str, str]) -> None:
        """
        Update the session variables.
        :param session_variables: The session variables.
        """
        self.session_variables.update(session_variables)
        self.code_interpreter.update_session_variables(self.session_variables)

    @tracing_decorator
    def chat(self, message: str) -> str:
        """
        Chat with the session.
        :param message: The message.
        :return: The response.
        """
        # create a new round
        round_id = str(uuid.uuid4())
        self.event_emitter.start_round(round_id)

        # create a user post
        user_post = Post.create(
            message=message,
            send_from="User",
            send_to="Planner",
        )

        # create a round
        round = Round(
            id=round_id,
            user_query=message,
            post_list=[user_post],
        )

        # add the round to the memory
        self.memory.add_round(round)

        # get the response from the planner
        planner_post_proxy = self.event_emitter.create_post_proxy("Planner")
        planner_post = self.planner.reply(
            memory=self.memory,
            post_proxy=planner_post_proxy,
        )
        round.add_post(planner_post)

        # if the planner sends the message to the code interpreter, get the response from the code interpreter
        if planner_post.send_to == "CodeInterpreter":
            code_interpreter_post = self.code_interpreter.reply(
                memory=self.memory,
            )
            round.add_post(code_interpreter_post)

            # if the code interpreter sends the message to the planner, get the response from the planner
            if code_interpreter_post.send_to == "Planner":
                planner_post_proxy = self.event_emitter.create_post_proxy("Planner")
                planner_post = self.planner.reply(
                    memory=self.memory,
                    post_proxy=planner_post_proxy,
                )
                round.add_post(planner_post)

        # end the round
        self.event_emitter.end_round(round_id)

        # get the response
        response = ""
        for post in round.post_list:
            if post.send_to == "User":
                response = post.message
                break

        return response

    def close(self) -> None:
        """
        Close the session.
        """
        self.code_interpreter.close()
        self.planner.close()


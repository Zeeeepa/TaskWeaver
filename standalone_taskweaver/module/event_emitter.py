import contextlib
from typing import Any, Callable, Dict, List, Optional

from standalone_taskweaver.memory import Attachment, Post
from standalone_taskweaver.memory.attachment import AttachmentType


class SessionEventHandler:
    """
    SessionEventHandler is used to handle session events.
    """

    def on_round_start(self, round_id: str) -> None:
        """
        Handle round start event.
        :param round_id: The round ID.
        """
        pass

    def on_round_end(self, round_id: str) -> None:
        """
        Handle round end event.
        :param round_id: The round ID.
        """
        pass

    def on_post_update(
        self,
        post: Post,
        status: Optional[str] = None,
    ) -> None:
        """
        Handle post update event.
        :param post: The post.
        :param status: The status.
        """
        pass

    def on_error(self, error: str) -> None:
        """
        Handle error event.
        :param error: The error.
        """
        pass


class PostEventProxy:
    """
    PostEventProxy is used to proxy post events.
    """

    def __init__(
        self,
        send_from: str,
        event_emitter: "SessionEventEmitter",
    ) -> None:
        self.post = Post.create(
            message="",
            send_from=send_from,
            send_to="Unknown",
        )
        self.event_emitter = event_emitter
        self.status: Optional[str] = None

    def update_message(
        self,
        message: str,
        is_end: bool = False,
    ) -> None:
        """
        Update the message.
        :param message: The message.
        :param is_end: Whether this is the end of the message.
        """
        self.post.message = message
        self.event_emitter.update_post(self.post, self.status)

    def update_send_to(self, send_to: str) -> None:
        """
        Update the send_to field.
        :param send_to: The send_to field.
        """
        self.post.send_to = send_to
        self.event_emitter.update_post(self.post, self.status)

    def update_status(self, status: str) -> None:
        """
        Update the status.
        :param status: The status.
        """
        self.status = status
        self.event_emitter.update_post(self.post, self.status)

    def update_attachment(
        self,
        content: Any,
        type: AttachmentType,
        message: Optional[str] = None,
        extra: Optional[Any] = None,
    ) -> None:
        """
        Update the attachment.
        :param content: The content.
        :param type: The type.
        :param message: The message.
        :param extra: The extra.
        """
        if message is not None:
            self.post.message = message
        attachment = Attachment(
            content=content,
            type=type,
            extra=extra,
        )
        self.post.add_attachment(attachment)
        self.event_emitter.update_post(self.post, self.status)

    def error(self, error: str) -> None:
        """
        Handle error.
        :param error: The error.
        """
        self.post.message = error
        self.event_emitter.update_post(self.post, "error")

    def end(self, message: Optional[str] = None) -> Post:
        """
        End the post.
        :param message: The message.
        :return: The post.
        """
        if message is not None:
            self.post.message = message
        self.event_emitter.update_post(self.post, "end")
        return self.post


class SessionEventEmitter:
    """
    SessionEventEmitter is used to emit session events.
    """

    def __init__(self) -> None:
        self.handlers: List[SessionEventHandler] = []

    def add_handler(self, handler: SessionEventHandler) -> None:
        """
        Add a handler.
        :param handler: The handler.
        """
        self.handlers.append(handler)

    def remove_handler(self, handler: SessionEventHandler) -> None:
        """
        Remove a handler.
        :param handler: The handler.
        """
        self.handlers.remove(handler)

    def start_round(self, round_id: str) -> None:
        """
        Start a round.
        :param round_id: The round ID.
        """
        for handler in self.handlers:
            handler.on_round_start(round_id)

    def end_round(self, round_id: str) -> None:
        """
        End a round.
        :param round_id: The round ID.
        """
        for handler in self.handlers:
            handler.on_round_end(round_id)

    def update_post(
        self,
        post: Post,
        status: Optional[str] = None,
    ) -> None:
        """
        Update a post.
        :param post: The post.
        :param status: The status.
        """
        for handler in self.handlers:
            handler.on_post_update(post, status)

    def emit_error(self, error: str) -> None:
        """
        Emit an error.
        :param error: The error.
        """
        for handler in self.handlers:
            handler.on_error(error)

    def create_post_proxy(self, send_from: str) -> PostEventProxy:
        """
        Create a post proxy.
        :param send_from: The send_from field.
        :return: The post proxy.
        """
        return PostEventProxy(send_from, self)

    @contextlib.contextmanager
    def handle_events_ctx(
        self,
        handler: Optional[SessionEventHandler] = None,
    ):
        """
        Handle events in a context.
        :param handler: The handler.
        """
        if handler is not None:
            self.add_handler(handler)
        try:
            yield
        finally:
            if handler is not None:
                self.remove_handler(handler)


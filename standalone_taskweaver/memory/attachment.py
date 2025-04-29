from enum import Enum
from typing import Any, Dict, Optional


class AttachmentType(str, Enum):
    """
    AttachmentType is used to specify the type of an attachment.
    """

    thought = "thought"
    reply_type = "reply_type"
    reply_content = "reply_content"
    verification = "verification"
    code_error = "code_error"
    execution_status = "execution_status"
    execution_result = "execution_result"
    artifact_paths = "artifact_paths"
    revise_message = "revise_message"
    init_plan = "init_plan"
    plan = "plan"
    current_plan_step = "current_plan_step"


class Attachment:
    """
    Attachment is used to store additional information in a post.
    """

    def __init__(
        self,
        content: Any,
        type: AttachmentType,
        extra: Optional[Any] = None,
    ) -> None:
        self.content = content
        self.type = type
        self.extra = extra

    def to_dict(self) -> Dict[str, Any]:
        """Convert the attachment to a dictionary."""
        return {
            "content": self.content,
            "type": self.type,
            "extra": self.extra,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Attachment":
        """Create an attachment from a dictionary."""
        return Attachment(
            content=data["content"],
            type=AttachmentType(data["type"]),
            extra=data.get("extra"),
        )


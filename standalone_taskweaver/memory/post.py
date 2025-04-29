import uuid
from typing import Any, Dict, List, Optional

from standalone_taskweaver.memory.attachment import Attachment, AttachmentType


class Post:
    """
    Post is used to store a message in a conversation.
    """

    def __init__(
        self,
        id: str,
        message: str,
        send_from: str,
        send_to: str,
        attachment_list: Optional[List[Attachment]] = None,
    ) -> None:
        self.id = id
        self.message = message
        self.send_from = send_from
        self.send_to = send_to
        self.attachment_list = attachment_list if attachment_list is not None else []

    def add_attachment(self, attachment: Attachment) -> None:
        """Add an attachment to the post."""
        self.attachment_list.append(attachment)

    def get_attachment(self, type: AttachmentType) -> List[Attachment]:
        """Get attachments of a specific type."""
        return [a for a in self.attachment_list if a.type == type]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the post to a dictionary."""
        return {
            "id": self.id,
            "message": self.message,
            "send_from": self.send_from,
            "send_to": self.send_to,
            "attachment_list": [a.to_dict() for a in self.attachment_list],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Post":
        """Create a post from a dictionary."""
        return Post(
            id=data["id"],
            message=data["message"],
            send_from=data["send_from"],
            send_to=data["send_to"],
            attachment_list=[Attachment.from_dict(a) for a in data["attachment_list"]],
        )

    @staticmethod
    def create(
        message: str,
        send_from: str,
        send_to: str,
    ) -> "Post":
        """Create a new post."""
        return Post(
            id=str(uuid.uuid4()),
            message=message,
            send_from=send_from,
            send_to=send_to,
        )


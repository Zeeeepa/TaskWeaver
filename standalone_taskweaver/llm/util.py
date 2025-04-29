from typing import Any, Dict, List, Optional, TypedDict


class ChatMessageType(TypedDict):
    """
    ChatMessageType is the type of a chat message.
    """

    role: str
    content: str
    image_urls: Optional[List[str]]


def format_chat_message(
    role: str,
    message: str,
    image_urls: Optional[List[str]] = None,
) -> ChatMessageType:
    """
    Format a chat message.
    :param role: The role.
    :param message: The message.
    :param image_urls: The image URLs.
    :return: The formatted chat message.
    """
    chat_message: Dict[str, Any] = {
        "role": role,
        "content": message,
    }
    if image_urls is not None and len(image_urls) > 0:
        chat_message["image_urls"] = image_urls
    return chat_message


from typing import Any, Dict, List, Optional

import yaml

from standalone_taskweaver.memory.round import Round


class Conversation:
    """
    Conversation is used to store all the rounds in a conversation.
    """

    def __init__(
        self,
        rounds: Optional[List[Round]] = None,
    ) -> None:
        self.rounds = rounds if rounds is not None else []

    def add_round(self, round: Round) -> None:
        """Add a round to the conversation."""
        self.rounds.append(round)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the conversation to a dictionary."""
        return {
            "rounds": [r.to_dict() for r in self.rounds],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Conversation":
        """Create a conversation from a dictionary."""
        return Conversation(
            rounds=[Round.from_dict(r) for r in data["rounds"]],
        )

    @staticmethod
    def init() -> "Conversation":
        """Initialize a conversation."""
        return Conversation()

    @staticmethod
    def from_yaml(path: str) -> "Conversation":
        """Load a conversation from a yaml file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return Conversation.from_dict(data)


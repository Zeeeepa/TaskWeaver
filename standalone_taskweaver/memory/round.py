from typing import Any, Dict, List, Optional

from standalone_taskweaver.memory.post import Post


class Round:
    """
    Round is used to store a round of conversation.
    """

    def __init__(
        self,
        id: str,
        user_query: str,
        post_list: Optional[List[Post]] = None,
    ) -> None:
        self.id = id
        self.user_query = user_query
        self.post_list = post_list if post_list is not None else []

    def add_post(self, post: Post) -> None:
        """Add a post to the round."""
        self.post_list.append(post)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the round to a dictionary."""
        return {
            "id": self.id,
            "user_query": self.user_query,
            "post_list": [p.to_dict() for p in self.post_list],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Round":
        """Create a round from a dictionary."""
        return Round(
            id=data["id"],
            user_query=data["user_query"],
            post_list=[Post.from_dict(p) for p in data["post_list"]],
        )


from typing import Dict, List, Optional, Set, Tuple

from standalone_taskweaver.memory.attachment import Attachment
from standalone_taskweaver.memory.conversation import Conversation
from standalone_taskweaver.memory.post import Post
from standalone_taskweaver.memory.round import Round
from standalone_taskweaver.memory.type_vars import RoleName, SharedMemoryEntryType


class SharedMemoryEntry:
    """
    SharedMemoryEntry is used to store a shared memory entry.
    """

    def __init__(
        self,
        entry_type: SharedMemoryEntryType,
        content: str,
    ) -> None:
        self.entry_type = entry_type
        self.content = content


class Memory:
    """
    Memory is used to store the memory of a conversation.
    """

    def __init__(self) -> None:
        self.conversation = Conversation()
        self.shared_memory: Dict[SharedMemoryEntryType, List[SharedMemoryEntry]] = {}

    def add_round(self, round: Round) -> None:
        """Add a round to the memory."""
        self.conversation.add_round(round)

    def get_rounds(self) -> List[Round]:
        """Get all rounds in the memory."""
        return self.conversation.rounds

    def get_role_rounds(
        self,
        role: RoleName,
        include_failure_rounds: bool = True,
    ) -> List[Round]:
        """
        Get rounds that involve a specific role.
        :param role: The role name.
        :param include_failure_rounds: Whether to include failure rounds.
        :return: The rounds.
        """
        role_rounds = []
        for round in self.conversation.rounds:
            is_role_round = False
            for post in round.post_list:
                if post.send_from == role or post.send_to == role:
                    is_role_round = True
                    break
            if is_role_round:
                role_rounds.append(round)
        return role_rounds

    def get_role_conversation(
        self,
        role_set: Set[RoleName],
        include_failure_rounds: bool = True,
    ) -> Conversation:
        """
        Get a conversation that involves specific roles.
        :param role_set: The set of role names.
        :param include_failure_rounds: Whether to include failure rounds.
        :return: The conversation.
        """
        role_rounds = []
        for round in self.conversation.rounds:
            is_role_round = False
            for post in round.post_list:
                if post.send_from in role_set or post.send_to in role_set:
                    is_role_round = True
                    break
            if is_role_round:
                role_rounds.append(round)
        return Conversation(role_rounds)

    def get_last_k_rounds(self, k: int) -> List[Round]:
        """
        Get the last k rounds in the memory.
        :param k: The number of rounds.
        :return: The rounds.
        """
        return self.conversation.rounds[-k:]

    def get_last_round(self) -> Optional[Round]:
        """
        Get the last round in the memory.
        :return: The round.
        """
        if len(self.conversation.rounds) > 0:
            return self.conversation.rounds[-1]
        return None

    def get_last_post(self) -> Optional[Post]:
        """
        Get the last post in the memory.
        :return: The post.
        """
        last_round = self.get_last_round()
        if last_round is not None and len(last_round.post_list) > 0:
            return last_round.post_list[-1]
        return None

    def add_shared_memory_entry(
        self,
        entry_type: SharedMemoryEntryType,
        content: str,
    ) -> None:
        """
        Add a shared memory entry.
        :param entry_type: The entry type.
        :param content: The content.
        """
        if entry_type not in self.shared_memory:
            self.shared_memory[entry_type] = []
        self.shared_memory[entry_type].append(
            SharedMemoryEntry(
                entry_type=entry_type,
                content=content,
            ),
        )

    def get_shared_memory_entries(
        self,
        entry_type: SharedMemoryEntryType,
    ) -> List[SharedMemoryEntry]:
        """
        Get shared memory entries of a specific type.
        :param entry_type: The entry type.
        :return: The entries.
        """
        return self.shared_memory.get(entry_type, [])


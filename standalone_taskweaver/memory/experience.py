import os
from typing import Dict, List, Optional, Set

from standalone_taskweaver.llm import LLMApi
from standalone_taskweaver.memory.conversation import Conversation
from standalone_taskweaver.memory.round import Round
from standalone_taskweaver.utils import read_yaml


class Experience:
    """
    Experience is used to store the experience of a conversation.
    """

    def __init__(
        self,
        rounds: List[Round],
    ) -> None:
        self.rounds = rounds

    @staticmethod
    def from_yaml(path: str) -> "Experience":
        """Load an experience from a yaml file."""
        conversation = Conversation.from_yaml(path)
        return Experience(
            rounds=conversation.rounds,
        )


class ExperienceGenerator:
    """
    ExperienceGenerator is used to generate experiences from the memory.
    """

    def __init__(
        self,
        llm_api: LLMApi,
        experience_dir: str,
    ) -> None:
        self.llm_api = llm_api
        self.experience_dir = experience_dir
        self.experience_cache: Dict[str, List[Experience]] = {}

    def load_experiences(
        self,
        query: str,
        role_set: Optional[Set[str]] = None,
        top_k: int = 1,
    ) -> List[Experience]:
        """
        Load experiences from the memory.
        :param query: The query to search for experiences.
        :param role_set: The set of roles to filter the experiences.
        :param top_k: The number of experiences to return.
        :return: The experiences.
        """
        if not os.path.exists(self.experience_dir):
            return []

        # get all experience files
        experience_files = [
            os.path.join(self.experience_dir, f)
            for f in os.listdir(self.experience_dir)
            if f.startswith("raw_exp_") and f.endswith(".yaml")
        ]

        if len(experience_files) == 0:
            return []

        # load all experiences
        experiences = []
        for exp_file in experience_files:
            try:
                exp = Experience.from_yaml(exp_file)
                experiences.append(exp)
            except Exception as e:
                print(f"Failed to load experience from {exp_file}: {e}")

        # filter experiences by role set
        if role_set is not None:
            filtered_experiences = []
            for exp in experiences:
                is_valid = True
                for round in exp.rounds:
                    for post in round.post_list:
                        if post.send_from not in role_set or post.send_to not in role_set:
                            is_valid = False
                            break
                    if not is_valid:
                        break
                if is_valid:
                    filtered_experiences.append(exp)
            experiences = filtered_experiences

        # sort experiences by similarity to query
        if len(experiences) > top_k:
            # TODO: implement similarity-based sorting
            experiences = experiences[:top_k]

        return experiences


import os
from typing import Dict, List, Optional, Set, Type

from injector import Binder, Module, inject, singleton

from standalone_taskweaver.config.config_mgt import AppConfigSource
from standalone_taskweaver.config.module_config import ModuleConfig
from standalone_taskweaver.logging import TelemetryLogger
from standalone_taskweaver.memory import Memory
from standalone_taskweaver.memory.experience import Experience, ExperienceGenerator
from standalone_taskweaver.module.event_emitter import SessionEventEmitter
from standalone_taskweaver.module.tracing import Tracing
from standalone_taskweaver.utils import read_yaml


class RoleConfig(ModuleConfig):
    def _configure(self) -> None:
        self._set_name("role")
        self.use_experience = self._get_bool("use_experience", False)
        self.use_example = self._get_bool("use_example", False)
        self.example_dir = self._get_path(
            "example_dir",
            os.path.join(self.src.app_base_path, "examples"),
        )


class RoleEntry:
    """
    RoleEntry is used to store the entry of a role.
    """

    def __init__(
        self,
        name: str,
        alias: str,
        module: Type,
        intro: str,
    ) -> None:
        self.name = name
        self.alias = alias
        self.module = module
        self.intro = intro


class RoleRegistry:
    """
    RoleRegistry is used to store all the roles.
    """

    def __init__(self) -> None:
        self.roles: Dict[str, RoleEntry] = {}

    def register(
        self,
        name: str,
        alias: str,
        module: Type,
        intro: str,
    ) -> None:
        """Register a role."""
        self.roles[name] = RoleEntry(
            name=name,
            alias=alias,
            module=module,
            intro=intro,
        )

    def get(self, name: str) -> Optional[RoleEntry]:
        """Get a role by name."""
        return self.roles.get(name, None)

    def get_role_name_list(self) -> List[str]:
        """Get all role names."""
        return list(self.roles.keys())


class RoleModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(RoleRegistry, to=RoleRegistry, scope=singleton)


class Role:
    """
    Role is the base class for all roles.
    """

    @inject
    def __init__(
        self,
        config: RoleConfig,
        logger: TelemetryLogger,
        tracing: Tracing,
        event_emitter: SessionEventEmitter,
        role_entry: Optional[RoleEntry] = None,
    ) -> None:
        self.config = config
        self.logger = logger
        self.tracing = tracing
        self.event_emitter = event_emitter
        self.role_entry = role_entry

        if role_entry is not None:
            self.alias = role_entry.alias
            self.intro = role_entry.intro
        else:
            self.alias = self.__class__.__name__
            self.intro = ""

        self.examples: List[Experience] = []
        self.experience: Optional[Experience] = None

    def set_alias(self, alias: str) -> None:
        """Set the alias of the role."""
        self.alias = alias

    def get_alias(self) -> str:
        """Get the alias of the role."""
        return self.alias

    def get_intro(self) -> str:
        """Get the introduction of the role."""
        return self.intro

    def role_load_example(
        self,
        memory: Memory,
        role_set: Optional[Set[str]] = None,
    ) -> None:
        """
        Load examples for the role.
        :param memory: The memory.
        :param role_set: The set of roles to filter the examples.
        """
        if not self.config.use_example:
            return

        if not os.path.exists(self.config.example_dir):
            return

        # get all example files
        example_files = [
            os.path.join(self.config.example_dir, f)
            for f in os.listdir(self.config.example_dir)
            if f.endswith(".yaml")
        ]

        if len(example_files) == 0:
            return

        # load all examples
        self.examples = []
        for example_file in example_files:
            try:
                example = Experience.from_yaml(example_file)
                self.examples.append(example)
            except Exception as e:
                self.logger.error(f"Failed to load example from {example_file}: {e}")

        # filter examples by role set
        if role_set is not None:
            filtered_examples = []
            for example in self.examples:
                is_valid = True
                for round in example.rounds:
                    for post in round.post_list:
                        if post.send_from not in role_set or post.send_to not in role_set:
                            is_valid = False
                            break
                    if not is_valid:
                        break
                if is_valid:
                    filtered_examples.append(example)
            self.examples = filtered_examples

    def role_load_experience(
        self,
        query: str,
        memory: Memory,
    ) -> None:
        """
        Load experiences for the role.
        :param query: The query to search for experiences.
        :param memory: The memory.
        """
        if not self.config.use_experience:
            return

        if not hasattr(self, "experience_generator") or self.experience_generator is None:
            return

        experiences = self.experience_generator.load_experiences(
            query=query,
            role_set={self.alias, "Planner", "User"},
            top_k=1,
        )

        if len(experiences) > 0:
            self.experience = experiences[0]
        else:
            self.experience = None

    def format_experience(
        self,
        template: str,
    ) -> str:
        """
        Format the experience for the prompt.
        :param template: The template.
        :return: The formatted experience.
        """
        if not self.config.use_experience or self.experience is None:
            return ""

        return template.format(
            ROLE_NAME=self.alias,
        )

    def close(self) -> None:
        """Close the role."""
        pass

